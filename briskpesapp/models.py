from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class Vendor(models.Model):
	class Meta:
		managed = False
		db_table = 'bp_vendor'
  	id = models.AutoField(primary_key=True)
  	name = models.CharField(max_length=255)
  	short_name = models.CharField(max_length=255)
	email_address = models.CharField(unique=True, max_length=255)
	phone_number = models.CharField(max_length=50)
	physical_address = models.CharField(max_length=200)
	api_key = models.CharField(max_length=255, null=False)
	is_active = models.BooleanField(default=True, null=False)
	owns_paybill = models.BooleanField(default=False, null=False)
	merchant_id = models.CharField(max_length=50)
	pass_key = models.CharField(max_length=255)
	date_joined = models.DateTimeField(auto_now_add=True)


# AuthUserMmanager
class AuthUserManager(BaseUserManager):
	def create_user(self, name, vendor_id, email_address, phone_number, password=None):
		if not email_address:
			raise ValueError('Email address must be provided')
		if not name:
			raise ValueError('Name must be provided')

		user = self.model(name=name, vendor_id=vendor_id, email_address=self.normalize_email(email_address), phone_number=phone_number)
		user.is_active = True
		user.set_password(password)
		user.save(using=self.db)
		return user

	def create_superuser(self, name, vendor_id, email_address, phone_number, password=None):
		user = self.create_user(name=name, vendor_id=vendor_id, email_address=self.normalize_email(email_address), phone_number=phone_number, password=password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self.db)
		return user


class User(AbstractBaseUser, PermissionsMixin):
  	class Meta:
		managed = False
		db_table = 'bp_user'
  	id = models.AutoField(primary_key=True)
  	vendor_id = models.IntegerField(default=0)
  	name = models.CharField(max_length=255, db_index=True)
  	email_address = models.CharField(max_length=255, unique=True)
  	phone_number = models.CharField(max_length=50)
  	date_joined = models.DateTimeField(auto_now_add=True)
  	is_active = models.BooleanField(default=True, null=False)
  	is_staff = models.BooleanField(default=False, null=False)

	objects = AuthUserManager()
	USERNAME_FIELD = 'email_address'
	REQUIRED_FIELDS = ['name', 'phone_number', 'vendor_id']

  	def get_full_name(self):
		return self.name

	def get_short_name(self):
		return self.name

	def __unicode__(self):
		return self.name


class Transaction(models.Model):
  class Meta:
		  managed = False
		  db_table = 'bp_transaction'
  id = models.AutoField(primary_key=True)
  vendor = models.ForeignKey(Vendor)
  order_id = models.CharField(max_length=255)
  msisdn = models.CharField(max_length=50)
  amount = models.IntegerField(default=0, null=False)
  trx_status = models.IntegerField(default=-1) # -1 pending, 0 success, 1 failure
  trx_id = models.CharField(max_length=255)
  channel = models.IntegerField(default=1) # 1 web, 2 android
  transaction_desc = models.TextField()
  mpesa_txt_date = models.DateTimeField()
  mpesa_trx_id = models.CharField(max_length=50)
  return_code = models.CharField(max_length=10)
  mpesa_desc = models.CharField(max_length=255)
  request_time = models.DateTimeField(auto_now_add=True)
  process_time = models.DateTimeField(auto_now=True)


class TransactionSuccess(models.Model):
  class Meta:
	  managed = False
	  db_table = 'bp_transaction_success'
  trans_id = models.IntegerField(primary_key=True)
  vendor = models.ForeignKey(Vendor)
  order_id = models.CharField(max_length=255)
  msisdn = models.CharField(max_length=50)
  amount_paid = models.IntegerField(default=0, null=False)
  amount_charged = models.DecimalField(max_digits=19, decimal_places=2)
  amount_available = models.DecimalField(max_digits=19, decimal_places=2)
  closing_balance = models.DecimalField(max_digits=19, decimal_places=2)
  trx_status = models.IntegerField(default=-1) # -1 pending, 0 success, 1 failure
  trx_id = models.CharField(max_length=255)
  channel = models.IntegerField(default=1) # 1 web, 2 android
  transaction_desc = models.TextField()
  mpesa_txt_date = models.DateTimeField()
  mpesa_trx_id = models.CharField(max_length=50)
  return_code = models.CharField(max_length=10)
  mpesa_desc = models.CharField(max_length=255)
  request_time = models.DateTimeField(auto_now=True)
  process_time = models.DateTimeField(auto_now=True)
  charge_time = models.DateTimeField(auto_now_add=True)


class TransactionFailed(models.Model):
  class Meta:
	  managed = False
	  db_table = 'bp_transaction_failed'
  trans_id = models.IntegerField(primary_key=True)
  vendor = models.ForeignKey(Vendor)
  order_id = models.CharField(max_length=255)
  msisdn = models.CharField(max_length=50)
  amount = models.IntegerField(default=0, null=False)
  trx_status = models.IntegerField(default=-1) # -1 pending, 0 success, 1 failure
  trx_id = models.CharField(max_length=255)
  channel = models.IntegerField(default=1) # 1 web, 2 android
  transaction_desc = models.TextField()
  return_code = models.CharField(max_length=10)
  mpesa_desc = models.CharField(max_length=255)
  request_time = models.DateTimeField(auto_now=True)
  process_time = models.DateTimeField(auto_now=True)


class Balance(models.Model):
  class Meta:
	  managed = False
	  db_table = 'bp_balance'
  id = models.AutoField(primary_key=True)
  vendor = models.ForeignKey(Vendor)
  balance = models.DecimalField(max_digits=19, decimal_places=2)
  last_modified = models.DateTimeField(auto_now_add=True)
