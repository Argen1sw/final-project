from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Alert


class AlertGeoSerializer(GeoFeatureModelSerializer):
    """
    Serializer to return Alert data as GeoJSON features.
    """
    class Meta:
        model = Alert
        geo_field = 'location'
        fields = (
            'id',
            'hazard_type',
            'effect_radius',
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
            'is_active',
        )
