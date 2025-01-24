from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Alert


class AlertGeoSerializer(GeoFeatureModelSerializer):
    """
    Serializer to return Alert data as GeoJSON features.
    """
    class Meta:
        model = Alert
        geo_field = 'location'  # Must match your geometry field name.
        fields = (
            'id',
            'description',
            'created_at',
            'updated_at',
            'deletion_time',
            'country',
            'city',
            'county',
            'reported_by',
            'source_url',
            'positive_votes',
            'negative_votes',
            'hazard_type',
            'is_active',
        )

class CreateAlertSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
