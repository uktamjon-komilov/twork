from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *


router = DefaultRouter()
router.register("otp", OtpViewSet, basename="otp")
router.register("user", UserViewSet, basename="user")
router.register("client", ClientViewSet, basename="client")
router.register("individual", IndividualViewSet, basename="individual")
router.register("legal-entity", LegalEntityViewSet, basename="legal-entity")


urlpatterns = [
    path("token/", JwtTokenApiView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    
    path("", include(router.urls))
]