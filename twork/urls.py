from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


api_info = openapi.Info(
    title="Teamwork API",
    default_version="v1",
)

schema_view = get_schema_view(
   api_info,
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
)

urlpatterns += [
    path("api/", include("api.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("rosetta/", include("rosetta.urls"))
    ]