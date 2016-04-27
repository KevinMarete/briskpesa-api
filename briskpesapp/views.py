from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'briskpesapp/index.html')

@csrf_exempt
def onlinecheckout(request):
	return HttpResponse("Data received")