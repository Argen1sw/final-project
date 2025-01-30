from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from .models import Alert
from django.contrib.gis.geos import Point


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
