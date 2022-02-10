from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import *
from api.errors_details import *


class OtpViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = Otp.objects.all()
    serializer_class = OtpSerializer

    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "code": openapi.Schema(type=openapi.TYPE_STRING, description="OTP code"),
            }
        )
    )
    @action(detail=True, methods=["post"], url_path="validate")
    def validate(self, request, pk=None):
        try:
            otp = Otp.objects.get(id=pk)
            now = timezone.now()
            if otp.is_expired(now):
                return Response(
                    {
                        "status": False,
                        "detail": OTP_EXPIRED
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not otp.check_code(request.data["code"]):
                return Response(
                    {
                        "status": False,
                        "detail": WRONG_OTP_CODE
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            otp.activate()
            otp.save()
            return Response(
                {
                    "status": True
                },
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {
                    "status": False,
                    "detail": OTP_NOT_FOUND
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ClientViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet
    ):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class IndividualViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer


class UserViewSet(
        mixins.UpdateModelMixin,
        GenericViewSet
    ):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    


class LegalEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = LegalEntity.objects.all()
    serializer_class = LegalEntitySerializer


class JwtTokenApiView(TokenObtainPairView):
    serializer_class = JwtTokenSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "phone": openapi.Schema(type=openapi.TYPE_STRING, description="Phone"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        user = User.objects.filter(phone=data["phone"])
        if not user.exists():
            return Response(
                {
                    "status": False,
                    "detail": USER_DOES_NOT_EXIST
                }
            )
        user = user.first()
        if not user.check_password(data["password"]):
            return Response(
                {
                    "status": False,
                    "detail": INCORRECT_PASSWORD
                }
            )
        token = RefreshToken.for_user(user)
        result = {
            "status": True,
            "access": str(token.access_token),
            "refresh": str(token),
            "client": None,
            "freelancer": None
        }
        if hasattr(user, "client"):
            client_serializer = ClientSerializer(user.client)
            result["client"] = {**client_serializer.data}
        elif hasattr(user, "freelancer"):
            pass
        return Response(result, status=status.HTTP_200_OK)