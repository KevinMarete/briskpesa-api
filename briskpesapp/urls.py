from django.conf.urls import url

from . import views

urlpatterns = [
    # API V1
    # ex: /v1/onlinecheckout
    url(r'^v1/onlinecheckout$', views.onlinecheckout, name='onlinecheckout'),
    # ex: /v1/checkout
    url(r'^v1/checkout$', views.process_checkout, name='checkout'),
    # ex: /v1/checkout
    url(r'^v1/poll$', views.poll, name='poll'),

    # ex: /gen-key
    url(r'^gen-key$', views.gen_key, name='gen-key'),
]