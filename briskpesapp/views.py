from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from models import Transaction, Vendor
from utils import is_valid_phone, sanitize_phone
import logging
from django.utils import timezone
import datetime
from checkout import send_payment_request, send_confirm_request, send_status_request, parser_process_callback
import json
import requests
import hashlib
import os

logger = logging.getLogger(__name__)


@csrf_exempt
def onlinecheckout(request):
	if request.method == 'POST':
		if (request.body != ""):
			p = parser_process_callback(request.body)
			# update transaction
			transaction = Transaction.objects.get(pk=int(p.MERCHANT_TRANSACTION_ID))
			transaction.return_code = p.RETURN_CODE
			transaction.mpesa_desc = p.DESCRIPTION
			transaction.process_time = timezone.now()
			if p.TRX_STATUS == "Success":
				transaction.mpesa_txt_date = p.MPESA_TRX_DATE + "+03" # date time
				transaction.mpesa_trx_id = p.MPESA_TRX_ID
				transaction.trx_status = 0
			else:
				transaction.trx_status = 1
			transaction.save()
	return HttpResponse("Data received")

@csrf_exempt
def process_checkout(request):
	if request.method == 'POST':
		# Get data

		if request.META.get('CONTENT_TYPE').lower() == "application/json":
			#json
			try:
				data = json.loads(request.body)
				phone = data.get('phone','')
				amount = data.get('amount',0)
				channel = data.get('channel',1)
				api_key = data.get('api_key','')
			except Exception as e:
				return JsonResponse({'status': False, 'desc': "Invalid json string"})

		else:
			#form
			phone = request.POST.get('phone','')
			amount = request.POST.get('amount',0)
			channel = request.POST.get('channel',1)
			api_key = request.POST.get('api_key','')

		phone = phone.strip()
		if phone == '' or amount == 0 or api_key.strip() == '':
			return JsonResponse({'status': False, 'desc': "Invalid/missing parameters"})

		if is_valid_phone(phone) == False:
			return JsonResponse({'status': False, 'desc': "Invalid phone number"})

		if isinstance(amount, int) == False and amount.isnumeric() == False:
			return JsonResponse({'status': False, 'desc': "Invalid amount"})

		if int(amount) < 10:
			return JsonResponse({'status': False, 'desc': "Amount must be greater than 10"})

		phone = sanitize_phone(phone)

		vendor = None
		try:
			vendor = Vendor.objects.get(api_key=api_key)
		except Vendor.DoesNotExist:
			return JsonResponse({'status': False, 'desc': "Invalid API key"})
		except Exception as e:
			logger.error("Error ocurred getting vendor " + str(e))
			return JsonResponse({'status': False, 'desc': "Invalid API key"})

		if vendor.is_active == False:
			return JsonResponse({'status': False, 'desc': "Vendor has been deactivated"})

		transaction = None
		try:
			transaction = Transaction(vendor=vendor, order_id=1, msisdn=phone, amount=int(amount), channel=int(channel))
			transaction.save()
		except Exception as e:
			logger.error("Error ocurred saving the transaction " + str(e))
			return JsonResponse({'status': False, 'desc': "Error ocurred saving the transaction"})

		res = send_payment_request(phone, amount, transaction.id, vendor.short_name)
		if res[0] == -1:
			logger.error("Sending payment request failed " + phone + " " + amount)
			return JsonResponse({'status': False, 'desc': 'Unknown error'})
	   	else:
	   		logger.info("Checkout response:- return code: " + res[0] + " description: " + res[1] + " transaction id: " + res[2])
	   		if res[0] == "00":
	   			transaction.trx_id = res[2]
				res2 = send_confirm_request(res[2])
				transaction.save()
				return JsonResponse({'status': True, 'trans_id': transaction.id, 'desc': 'Ok'})
			else:
				transaction.return_code = res[0]
				transaction.mpesa_desc = res[1]
				transaction.trx_id = res[2]
				transaction.trx_status = 1
				transaction.save()
				return JsonResponse({'status': False, 'desc': res[1]})

	return HttpResponse("GET: Echo back")


@csrf_exempt
def poll(request):
	if request.method == 'POST':
		# Get data
		if request.META.get('CONTENT_TYPE').lower() == "application/json":
			#json
			try:
				data = json.loads(request.body)
				trans_id = data.get('trans_id',0)
				channel = data.get('channel',1)
				api_key = data.get('api_key','')
			except Exception as e:
				return JsonResponse({'status': False, 'desc': "Invalid json string"})
		else:
			#form
			trans_id = request.POST.get('trans_id',0)
			channel = request.POST.get('channel',1)
			api_key = request.POST.get('api_key','')


		if trans_id == 0 or api_key.strip() == '':
			return JsonResponse({'status': False, 'desc': "Invalid/missing parameters"})

		if isinstance(trans_id, int) == False and trans_id.isnumeric() == False:
			return JsonResponse({'status': False, 'desc': "Invalid transaction id"})

		try:
			vendor = Vendor.objects.get(api_key=api_key)
		except Vendor.DoesNotExist:
			return JsonResponse({'status': False, 'desc': "Invalid API key"})

		try:
			transaction = Transaction.objects.get(pk=int(trans_id), vendor_id=vendor.id)
		except Transaction.DoesNotExist:
			return JsonResponse({'status': 2, 'desc': "Transaction does not exist"})
		
		if transaction.trx_status == 0:
			return JsonResponse({'status': 0, 'mpesa_code': transaction.mpesa_trx_id})
		elif transaction.trx_status == 1:
			return JsonResponse({'status': transaction.trx_status, 'desc': transaction.mpesa_desc})
		else:
			diff = timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()) - transaction.request_time
			if diff.seconds > 120: # 2 minutes, assume expired
				return JsonResponse({'status': 1, 'desc': "Transaction expired"})
			elif diff.seconds > 60: # 1 minute, poll safaricom
				# check status
				res = send_status_request(transaction.trx_id)
				
				if res[4] == "Pending":
					return JsonResponse({'status': transaction.trx_status})

				# update transaction
				transaction.return_code = res[5]
				transaction.mpesa_desc = res[6]
				transaction.process_time = timezone.now()

				if res[4] == "Success":
					transaction.mpesa_txt_date = res[2] + "+03" # date time
					transaction.mpesa_trx_id = res[3]
					transaction.trx_status = 0
					transaction.save()
					return JsonResponse({'status': 0, 'mpesa_code': transaction.mpesa_trx_id})

				elif res[4] == "Failed":
					transaction.trx_status = 1
					transaction.save()
					return JsonResponse({'status': transaction.trx_status, 'desc': transaction.mpesa_desc})

				return JsonResponse({'status': transaction.trx_status})
			else:
				return JsonResponse({'status': transaction.trx_status, 'desc': "Transaction Pending"})
	return HttpResponse("GET: Echo back")


@csrf_exempt
def gen_key(request):
	if request.method == 'POST':
		# Get data
		if request.META.get('CONTENT_TYPE').lower() == "application/json":
			#json
			data = json.loads(request.body)
			api_key = data.get('api_key','')
		else:
			#form
			api_key = request.POST.get('api_key','')

		try:
			vendor = Vendor.objects.get(api_key=api_key, id = 1)
		except Vendor.DoesNotExist:
			return JsonResponse({'status': False, 'desc': "Invalid API key"})

		new_key = hashlib.sha256(os.urandom(128)).hexdigest()
		return JsonResponse({'status': True, 'key': new_key, 'desc': 'Ok'})
		

	return HttpResponse("GET: Echo back")