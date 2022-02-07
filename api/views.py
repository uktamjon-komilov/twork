from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from api.serializers import *


class OtpViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = Otp.objects.all()
    serializer_class = OtpSerializer
    
    @action(detail=True, methods=["post"], url_path="validate")
    def validate(self, request, pk=None):
        try:
            otp = Otp.objects.get(id=pk)
            now = timezone.now()
            if otp.is_expired(now) or not otp.check_code(request.data["code"]):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            otp.activate()
            otp.save()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ClientViewSet(
        mixins.CreateModelMixin,
        GenericViewSet
    ):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer