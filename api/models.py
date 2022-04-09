from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from parler.models import TranslatableModel, TranslatedFields
from mptt.models import MPTTModel
from taggit.managers import TaggableManager

from api.managers import *
from api.services import OtpService
from api.constants import *
from api.utils import *


class Otp(models.Model):
    code = models.CharField(max_length=8, verbose_name=_("Otp code"), blank=True)
    phone = models.CharField(max_length=20, verbose_name=_("Phone number"))
    activated = models.BooleanField(default=False, verbose_name=_("Activated"))
    expires_in = models.DateTimeField(null=True, blank=True, verbose_name=_("Expires in"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        (INDIVIDUAL, _(INDIVIDUAL.capitalize().replace("_", " "))),
        (LEGAL_ENTITY, _(LEGAL_ENTITY.capitalize().replace("_", " "))),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client", verbose_name=_("User"))
    fullname = models.CharField(max_length=125, verbose_name=_("Fullname"))
    balance = models.FloatField(default=0.0)
    coins = models.IntegerField(default=0)
    client_type = models.CharField(max_length=30, choices=CLIENT_TYPE_CHOICES, null=True, verbose_name=_("Client type"))
    type_related_info = models.IntegerField(null=True, verbose_name=_("Related info"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        clients = Client.objects.filter(pk=self.client)
        for client in clients:
            client.set_legal_entity(0)
            client.save()
        super(LegalEntity, self).delete(*args, **kwargs)


class ProjectCategory(MPTTModel, TranslatableModel):
    parent = models.ForeignKey("self", related_name="children", on_delete=models.SET_NULL, null=True, blank=True)

    translations = TranslatedFields(
        title=models.CharField(blank=False, default="", max_length=128),
    )

    slug=models.SlugField(blank=False, default="", max_length=128)

    objects = CategoryManager()

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class FreelancerCategory(MPTTModel, TranslatableModel):
    parent = models.ForeignKey("self", related_name="children", on_delete=models.SET_NULL, null=True, blank=True)

    translations = TranslatedFields(
        title=models.CharField(blank=False, default="", max_length=128),
    )

    slug=models.SlugField(blank=False, default="", max_length=128)

    objects = CategoryManager()

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)


class ProjectInusrancePayment(models.Model):
    PAYMENT_TYPES = [
        ("bank_card", _("Bank card")),
        ("payme", _("Payme")),
        ("click", _("Click")),
    ]
    type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.FloatField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    card_expiry_month = models.CharField(max_length=2, null=True, blank=True)
    card_expiry_year = models.CharField(max_length=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Project(models.Model):
    STATUS = [
        ("unpublished", _("Not published")),
        ("published", _("Published")),
        ("working", _("Working")),
        ("finished", _("Not finished")),
    ]
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, verbose_name=_("Project title"))
    project_category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True)
    freelancer_category = models.ForeignKey(FreelancerCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(verbose_name=_("Description"))
    price_negotiatable = models.BooleanField(default=False)
    price = models.FloatField(default=0.0)
    deadline_negotiatable = models.BooleanField(default=False)
    deadline = models.DateField(null=True, blank=True)
    insurance_payment = models.ForeignKey(ProjectInusrancePayment, on_delete=models.SET_NULL, null=True)
    pro_task = models.BooleanField(default=False, verbose_name=_("Only pro accounts can see"))
    status = models.CharField(max_length=30, choices=STATUS, default=STATUS[0][0], verbose_name=_("Project status"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()


class ProjectPhoto(models.Model):
    photo = models.FileField(upload_to="images/project/")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="photos")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectFile(models.Model):
    file = models.FileField(upload_to="files/project/")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class TempFile(models.Model):
    file = models.FileField(upload_to="files/temp/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)