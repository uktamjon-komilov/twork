from wsgiref.validate import validator
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField


from api.models import *
from api.mixins import TranslatedSerializerMixin
from api.validators import validate_freelancer_category_id, validate_project_category_id, validate_status_client_project


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


class VariableModelSerializer(serializers.ModelSerializer):
    label = "-"
    allow_null = True



class TransModelSerializer(
    VariableModelSerializer,
    TranslatedSerializerMixin,
    TranslatableModelSerializer
):
    pass


class IndividualGetSerializer(VariableModelSerializer):
    class Meta:
        model = Individual
        fields = "__all__"


class IndividualUpdateSerializer(VariableModelSerializer):
    class Meta:
        model = Individual
        exclude = ["client"]


class IndividualCreateSerializer(VariableModelSerializer):
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


class LegalEntityGetSerializer(VariableModelSerializer):
    class Meta:
        model = LegalEntity
        fields = "__all__"


class LegalEntityUpdateSerializer(VariableModelSerializer):
    class Meta:
        model = LegalEntity
        exclude = ["client"]


class LegalEntityCreateSerializer(VariableModelSerializer):
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


class ClientGetSerializer(VariableModelSerializer):
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
                return {**IndividualGetSerializer(individual).data}
        if obj.client_type == LEGAL_ENTITY:
            legal_entity = LegalEntity.objects.filter(id=obj.type_related_info)
            if legal_entity.exists():
                legal_entity = legal_entity.first()
                return {**LegalEntityGetSerializer(legal_entity).data}
        return None


class ClientCreateSerializer(VariableModelSerializer):
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


class ClientUpdateSerializer(VariableModelSerializer):

    class Meta:
        model = Client
        fields = ["id", "fullname", "client_type", "type_related_info"]
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


class JwtTokenSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        phone = attrs.pop("phone", None)
        if phone:
            attrs["phone"] = clean_phone(phone)
        return super().validate(attrs)


class TempFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempFile
        fields = ["id", "file"]


class ProjectCategorySerializer(TransModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProjectCategory)

    class Meta:
        model = ProjectCategory
        fields = ["id", "translations", "slug"]


class FreelancerCategorySerializer(TransModelSerializer):
    translations = TranslatedFieldsField(shared_model=FreelancerCategory)

    class Meta:
        model = FreelancerCategory
        fields = ["id", "translations", "slug"]


class ProjectCreateUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    project_category = serializers.IntegerField(validators=[validate_project_category_id])
    freelancer_category = serializers.IntegerField(validators=[validate_freelancer_category_id])
    worker_type = serializers.CharField(max_length=255)
    price_negotiatable = serializers.BooleanField(default=False)
    price = serializers.FloatField()
    deadline_negotiatable = serializers.BooleanField(default=False)
    deadline = serializers.DateField()
    pro_task = serializers.BooleanField(default=False)
    status = serializers.CharField(max_length=255, validators=[validate_status_client_project])
    files = serializers.ListField()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        project_category_id = attrs.pop("project_category")
        try:
            project_category = ProjectCategory.objects.get(id=project_category_id)
            attrs["project_category"] = project_category
        except:
            raise serializers.ValidationError("Project category with the ID ({}) does not exist.".format(project_category_id))
        
        freelancer_category_id = attrs.pop("freelancer_category")
        try:
            freelancer_category = FreelancerCategory.objects.get(id=freelancer_category_id)
            attrs["freelancer_category"] = freelancer_category
        except:
            raise serializers.ValidationError("Freelancer category with the ID ({}) does not exist.".format(freelancer_category_id))
        
        file_ids = attrs["files"]
        existing_files = []
        for _id in file_ids:
            try:
                temp_file = TempFile.objects.get(id=_id)
                existing_files.append(temp_file)
            except:
                pass
        attrs["files"] = existing_files
        
        return attrs


class ProjectGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"