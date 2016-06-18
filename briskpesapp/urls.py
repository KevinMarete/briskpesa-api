from django.conf.urls import url

from . import views

urlpatterns = [
	# ex: /
    url(r'^$', views.index, name='index'),
    # ex: /onlinecheckout
    url(r'^onlinecheckout$', views.onlinecheckout, name='onlinecheckout'),
    # ex: /checkout
    url(r'^checkout$', views.process_checkout, name='checkout'),
    # ex: /checkout
    url(r'^poll$', views.poll, name='poll'),
    # ex: /demo-checkout
    url(r'^demo-checkout$', views.demo_checkout, name='demo-checkout'),
    # ex: /demo-poll
    url(r'^demo-poll$', views.demo_poll, name='demo-poll'),
    # ex: /gen-key
    url(r'^gen-key$', views.gen_key, name='gen-key'),

    # API V1
    # ex: /v1/onlinecheckout
    url(r'^v1/onlinecheckout$', views.onlinecheckout, name='onlinecheckout'),
    # ex: /v1/checkout
    url(r'^v1/checkout$', views.process_checkout, name='checkout'),
    # ex: /v1/checkout
    url(r'^v1/poll$', views.poll, name='poll'),
]