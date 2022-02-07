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
        fields = ["id", "phone", "password"]
        write_only_fields = ["password"]


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Client
        fields = ["id", "user", "fullname", "client_type", "type_related_info"]
        extra_kwargs = {
            "client_type": {
                "required": False
            },
            "type_related_info": {
                "read_only": True
            }
        }
    
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            validated_data["user"] = user
            return super().create(validated_data)
        return None