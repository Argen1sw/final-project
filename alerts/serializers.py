# Django imports
from rest_framework import serializers
from django.forms.models import model_to_dict
from rest_framework_gis.serializers import GeoFeatureModelSerializer

# Local imports
from .models import Alert

class AlertGeoSerializer(GeoFeatureModelSerializer):
    """
    Serializer to return Alert data as GeoJSON features.
    """
    hazard_type = serializers.SerializerMethodField()
    hazard_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        geo_field = 'location'
        fields = (
            'id',
            'effect_radius',
            'description',
            'created_at',
            'updated_at',
            'soft_deletion_time',
            'country',
            'city',
            'county',
            'reported_by',
            'source_url',
            'positive_votes',
            'negative_votes',
            'is_active',
            'hazard_type',
            'hazard_details',
        )

    def get_hazard_type(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_hazard_details(self, obj):
        if obj.hazard_details:
            return model_to_dict(obj.hazard_details)
        return None