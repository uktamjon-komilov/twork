from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from api.managers import UserManager
from api.services import OtpService
from api.constants import *
from api.utils import *


class Otp(models.Model):
    code = models.CharField(max_length=8, verbose_name=_("Otp code"), blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone number"))
    activated = models.BooleanField(default=False, verbose_name=_("Activated"))
    expires_in = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires in"))

    def __str__(self):
        return "OTP {} was sent to {}".format(self.code, self.phone)
    
    def save(self, *args, **kwargs):
        self.phone = clean_phone(self.phone)
        if self._state.adding:
            self.code = generate_code()
            self.expires_in = timezone.now() + timezone.timedelta(minutes=1)
            OtpService(self)
        return super(Otp, self).save(*args, **kwargs)
    
    def is_expired(self, datetime):
        return self.expires_in < datetime or self.activated
    
    def activate(self):
        self.activated = True
    
    def check_code(self, code):
        return self.code == str(code)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True, verbose_name=_("Phone number"))
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return getattr(self, self.USERNAME_FIELD)
    
    @property
    def username(self):
        return getattr(self, self.USERNAME_FIELD)
    
    def save(self, *args, **kwargs):
        self.phone = clean_phone(self.phone)
        return super().save(*args, **kwargs)


class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        (INDIVIDUAL, _(INDIVIDUAL.title())),
        (INDIVIDUAL, _(INDIVIDUAL.title())),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client", verbose_name=_("User"))
    fullname = models.CharField(max_length=125, verbose_name=_("Fullname"))
    client_type = models.CharField(max_length=30, choices=CLIENT_TYPE_CHOICES, null=True, verbose_name=_("Client type"))
    type_related_info = models.IntegerField(null=True, verbose_name=_("Related info"))

    def set_individual(self, id):
        self.type_related_info = id
        self.client_type = self.CLIENT_TYPE_CHOICES[0][0]
    
    def set_legal_entity(self, id):
        self.type_related_info = id
        self.client_type = self.CLIENT_TYPE_CHOICES[1][0]
    
    def delete(self, *args, **kwargs):
        individual = Individual.objects.filter(client=self.id)
        individual.delete()
        return super().delete(*args, **kwargs)


class Individual(models.Model):
    client = models.IntegerField(default=0)
    fullname = models.CharField(max_length=125, verbose_name=_("Fullname"))
    email = models.EmailField(max_length=255, null=True, blank=True, verbose_name=_("Email"))
    passport_series = models.CharField(max_length=10, verbose_name=_("Passport series"))
    passport_number = models.CharField(max_length=20, verbose_name=_("Passport number"))
    passport_given_date = models.DateField(verbose_name=_("Passport given date"))
    passport_issued_address = models.CharField(max_length=255, verbose_name=_("Passport issued address"))
    country = models.CharField(max_length=255, verbose_name=_("Country"))
    region = models.CharField(max_length=255, verbose_name=_("Region"))
    city = models.CharField(max_length=255, verbose_name=_("City"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))

    def delete(self, *args, **kwargs):
        clients = Client.objects.filter(pk=self.client)
        for client in clients:
            client.set_individual(0)
            client.save()
        super(Individual, self).delete(*args, **kwargs)


class LegalEntity(models.Model):
    client = models.IntegerField(default=0)
    fullname = models.CharField(max_length=125, verbose_name=_("Fullname"))
    company = models.CharField(max_length=255, verbose_name=_("Company"))
    bank_name = models.CharField(max_length=255, verbose_name=_("Bank name"))
    bank_account = models.CharField(max_length=255, verbose_name=_("Bank account"))
    mfo = models.CharField(max_length=255, verbose_name=_("MFO"))
    inn = models.CharField(max_length=255, verbose_name=_("INN"))
    ifut = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("IFUT"))
    country = models.CharField(max_length=255, verbose_name=_("Country"))
    region = models.CharField(max_length=255, verbose_name=_("Region"))
    city = models.CharField(max_length=255, verbose_name=_("City"))
    post_code = models.CharField(max_length=20, verbose_name=_("Post code"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    telegram_phone = models.CharField(max_length=20, verbose_name=_("Telegram phone"))
    email = models.EmailField(max_length=255, verbose_name=_("Email"))