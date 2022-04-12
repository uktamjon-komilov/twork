from rest_framework.viewsets import mixins, GenericViewSet, ModelViewSet
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


class UserViewSet(
        mixins.UpdateModelMixin,
        GenericViewSet
    ):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
            client_serializer = ClientGetSerializer(user.client)
            result["client"] = {**client_serializer.data}
        elif hasattr(user, "freelancer"):
            pass
        return Response(result, status=status.HTTP_200_OK)


class ClientViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet
    ):
    queryset = Client.objects.all()
    serializer_class = ClientCreateSerializer
    
    def get_serializer(self, *args, **kwargs):
        if self.action in ["list", "retrive"]:
            return ClientGetSerializer
        elif self.action in ["update", "partial_update"]:
            return ClientUpdateSerializer
        return ClientCreateSerializer
    
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Client.objects.none()
        else:
            print("hi")
        return super().get_queryset()


class LegalEntityViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet
    ):
    queryset = LegalEntity.objects.all()
    
    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return LegalEntityGetSerializer
        elif self.action in ["update", "partial_update"]:
            return LegalEntityUpdateSerializer
        return LegalEntityCreateSerializer
    
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return LegalEntity.objects.none()
        return super().get_queryset()


class IndividualViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet
    ):
    queryset = Individual.objects.all()

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return IndividualGetSerializer
        elif self.action in ["update", "partial_update"]:
            return IndividualUpdateSerializer
        return IndividualCreateSerializer
    
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Individual.objects.none()
        return super().get_queryset()


class TempFileCreateDeleteViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet
    ):
    queryset = TempFile.objects.all()
    serializer_class = TempFileSerializer


class ProjectCategoryListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer


class FreelancerCategoryListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = FreelancerCategory.objects.all()
    serializer_class = FreelancerCategorySerializer


class WorkerTypeListViewSet(
        mixins.ListModelMixin,
        GenericViewSet
    ):
    queryset = None
    serializer_class = None

    def list(self, request, *args, **kwargs):
        result = []
        for item in WORKER_TYPE:
            result.append({
                "slug": item[0],
                "title": item[1]
            })
        return Response(result)


class ProjectCreateUpdateViewSet(ModelViewSet):
    queryset = Project.objects.all()
    
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProjectCreateUpdateSerializer
        return ProjectGetSerializer
    

    def create(self, request, *args, **kwargs):
        serialized = self.get_serializer(data=request.data)
        serialized.is_valid(raise_exception=True)
        files = serialized.validated_data.pop("files", None)
        project = serialized.save()

        if files:
            for file in files:
                ProjectFile(file=file.file, project=project).save()
        
        serializer = ProjectGetSerializer(project)

        return Response(serializer.data, status=status.HTTP_201_CREATED)