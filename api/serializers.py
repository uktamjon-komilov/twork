from functools import partial
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
        extra_kwargs = {
            "password": {
                "required": False,
                "write_only": True,
                "read_only": False
            }
        }
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = Client
        fields = ["id", "user", "fullname", "client_type", "type_related_info"]
        extra_kwargs = {
            "client_type": {
                "required": False,
                "read_only": True
            },
            "type_related_info": {
                "read_only": True
            },
            "user": {
                "required": False
            },
            "fullname": {
                "required": False
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


class IndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = "__all__"

    def create(self, validated_data):
        client_id = validated_data.get("client", 0)
        individual = super().create(validated_data)
        if client_id:
            client = Client.objects.filter(id=client_id)
            if client.exists():
                client = client.first()
                client.set_individual(individual.id)
                client.save()
                individual.client = client_id
            else:
                individual.client = 0
            individual.save()
        return individual