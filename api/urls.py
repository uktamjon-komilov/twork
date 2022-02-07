from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
router.register("otp", OtpViewSet, basename="otp")


urlpatterns = [
    path("", include(router.urls))
]