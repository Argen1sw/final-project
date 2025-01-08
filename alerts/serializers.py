from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Alert


class AlertSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Alert
        geo_field = "location"
        fields = [
            "id", "title", "description", "created_at",
            "hazard_type", "severity", "country", "city", "county",
            "reported_by", "source_url"
        ]


class CreateAlertSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
