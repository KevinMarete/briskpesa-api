from django.conf.urls import url

from . import views

urlpatterns = [
	# ex: /
    url(r'^$', views.index, name='index'),
    # ex: /onlinecheckout
    url(r'^onlinecheckout$', views.onlinecheckout, name='onlinecheckout'),
    # ex: /testonlinecheckout
    url(r'^testonlinecheckout$', views.onlinecheckout, name='testonlinecheckout'),    
]