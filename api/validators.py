from rest_framework import serializers

from api.models import FreelancerCategory, ProjectCategory


def validate_status_client_project(value):
    if not value in ["unpublished", "published"]:
        raise serializers.ValidationError("You can either choose an option between 'unpublished' or 'published'")


def validate_project_category_id(value):
    try:
        ProjectCategory.objects.get(id=value)
    except:
        raise serializers.ValidationError("You should provide an existing project category ID")


def validate_freelancer_category_id(value):
    try:
        FreelancerCategory.objects.get(id=value)
    except:
        raise serializers.ValidationError("You should provide an existing freelancer category ID")