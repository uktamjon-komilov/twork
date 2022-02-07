from rest_framework import serializers

from api.models import *


class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ["id", "phone", "expires_in", "activated"]
        read_only_fields = ["activated", "expires_in"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "password", ""]
        write_only_fields = ["password"]


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    type_related_info_id = models.IntegerField()

    class Meta:
        model = Client
        fields = ["id", "user", "fullname", "client_type", "type_related_info_id", "type_related_info"]
        extra_kwargs = {
            "client_type": {
                "required": False
            },
            "type_related_info_id": {
                "required": False,
                "write_only": True
            },
            "type_related_info": {
                "read_only": True
            }
        }