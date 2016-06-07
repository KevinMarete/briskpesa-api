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
]