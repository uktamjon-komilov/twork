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
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


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


class LegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalEntity
        fields = "__all__"

    def create(self, validated_data):
        client_id = validated_data.get("client", 0)
        legal_entity = super().create(validated_data)
        if client_id:
            client = Client.objects.filter(id=client_id)
            if client.exists():
                client = client.first()
                client.set_legal_entity(legal_entity.id)
                client.save()
                legal_entity.client = client_id
            else:
                legal_entity.client = 0
            legal_entity.save()
        return legal_entity


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    details = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ["id", "user", "fullname", "client_type", "type_related_info", "details"]
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
            },
            "details": {
                "read_only": True
            }
        }
    
    def get_details(self, obj):
        if obj.client_type == INDIVIDUAL:
            individual = Individual.objects.filter(id=obj.type_related_info)
            if individual.exists():
                individual = individual.first()
                return {**IndividualSerializer(individual).data}
        if obj.client_type == LEGAL_ENTITY:
            legal_entity = LegalEntity.objects.filter(id=obj.type_related_info)
            if legal_entity.exists():
                legal_entity = legal_entity.first()
                return {**LegalEntitySerializer(legal_entity).data}
        return None
    
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            validated_data["user"] = user
            return super().create(validated_data)
        return None
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        return super().update(instance, validated_data)


class JwtTokenSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone = attrs.pop("phone", None)
        if phone:
            attrs["phone"] = clean_phone(phone)
        return super().validate(attrs)