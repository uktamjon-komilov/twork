from django.contrib import admin

from api.models import *


admin.site.register(Otp)
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Individual)
admin.site.register(LegalEntity)