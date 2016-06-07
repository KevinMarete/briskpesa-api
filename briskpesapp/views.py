from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from models import Transaction, Vendor
import logging
from django.utils import timezone
import datetime
from checkout import send_payment_request, send_confirm_request, parser_process_callback
import json
import requests

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'briskpesapp/index.html')

@csrf_exempt
def onlinecheckout(request):
	if request.method == 'POST':
		if (request.body != ""):
			p = parser_process_callback(request.body)
			# update transaction
			transaction = Transaction.objects.get(pk=int(p.MERCHANT_TRANSACTION_ID))
			transaction.return_code = p.RETURN_CODE
			transaction.mpesa_desc = p.DESCRIPTION
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
			data = json.loads(request.body)
			phone = data.get('phone','')
			amount = data.get('amount',0)
			api_key = data.get('api_key','')
		else:
			#form
			phone = request.POST.get('phone','')
			amount = request.POST.get('amount',0)
			api_key = request.POST.get('api_key','')

		if phone.strip() == '' or amount == 0 or api_key.strip() == '':
			return JsonResponse({'status': False, 'desc': "Invalid/missing parameters"})

		try:
			vendor = Vendor.objects.get(api_key=api_key)
		except Vendor.DoesNotExist:
			return JsonResponse({'status': False, 'desc': "Invalid API key"})			

		transaction = Transaction(vendor=vendor, order_id=1, msisdn=phone, amount=int(amount))
		transaction.save()

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
			data = json.loads(request.body)
			trans_id = data.get('trans_id',0)
			api_key = data.get('api_key','')
		else:
			#form
			trans_id = request.POST.get('trans_id',0)
			api_key = request.POST.get('api_key','')


		if trans_id == 0 or api_key.strip() == '':
			return JsonResponse({'status': False, 'desc': "Invalid/missing parameters"})

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
			if diff.seconds > 90: # 1 and 1/2 minutes, assume failed
				return JsonResponse({'status': 1, 'desc': "Transaction expired"})
			else:
				return JsonResponse({'status': transaction.trx_status})
	return HttpResponse("GET: Echo back")


@csrf_exempt
def demo_checkout(request):
	if request.method == 'POST':
		# Get data
		phone = request.POST.get('phone','')
		amount = request.POST.get('amount',0)

		url = 'https://briskpesa.com/checkout'
		api_key = '490cc963938029b5510bbf9932d1650ef80a86096b00ae8a0e9b84e6154b64b4'
		payload = {'phone': phone, 'amount': amount, 'api_key': api_key}
		headers = {'content-type': 'application/json'}

		r = requests.post(url, data=json.dumps(payload), headers=headers)
		return JsonResponse(json.loads(r.text))
		

	return HttpResponse("GET: Echo back")


@csrf_exempt
def demo_poll(request):
	if request.method == 'POST':
		# Get data
		trans_id = data.get('trans_id',0)

		url = 'https://briskpesa.com/poll'
		api_key = '490cc963938029b5510bbf9932d1650ef80a86096b00ae8a0e9b84e6154b64b4'
		payload = {'phone': phone, 'amount': amount, 'api_key': api_key}
		headers = {'content-type': 'application/json'}

		r = requests.post(url, data=json.dumps(payload), headers=headers)
		return JsonResponse(json.loads(r.text))
		

	return HttpResponse("GET: Echo back")