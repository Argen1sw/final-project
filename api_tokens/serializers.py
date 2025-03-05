#Django Imports
from rest_framework import serializers
from django.forms.models import model_to_dict
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point
from django.contrib.contenttypes.models import ContentType

# Local Imports
from alerts.models import (Alert, Earthquake, Flood, Fire, Tornado)


HAZARD_MODEL_MAPPING = {
    'earthquake': Earthquake,
    'flood': Flood,
    'tornado': Tornado,
    'fire': Fire,
}

class ListAlertSerializer(GeoFeatureModelSerializer):
    """
    Serializer to return Alert data as GeoJSON features.
    """
    reported_by = serializers.SlugRelatedField(read_only=True, slug_field='username')
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
    

class CreateAlertSerializer(serializers.ModelSerializer):
    """
    Serializer to create an Alert record.
    
    * Accepts latitude, longitude, hazard type, and hazard data.
    * Reverse geocodes the location to get country, city, etc.
    * Creates a hazard type instance.
    * Creates an Alert record.
    * Returns the created Alert record.
    """    
    
    lat = serializers.FloatField(write_only=True)
    lng = serializers.FloatField(write_only=True)
    hazard_type = serializers.CharField(write_only=True)
    hazard_data = serializers.DictField(write_only=True, required=False)
    effect_radius = serializers.IntegerField(required=False)

    class Meta:
        model = Alert
        # These are the fields that the client is expected to send.
        # Other fields (like country, city, etc.) will be generated automatically.
        fields = (
            'lat', # Latitude - Required
            'lng', # Longitude - Required
            'hazard_type', # Type of hazard - Required
            'effect_radius', # Radius of effect in meters - Optional as default will be set
            'description', # Description of the alert - Optional
            'source_url', # Source URL for the alert - Optional
            'hazard_data', # Additional data for the hazard - Optional
        )

    def validate_effect_radius(self, value):
        if value > 100000 or value < 0:  # 100 km = 100,000 meters
            raise serializers.ValidationError("The radius of effect cannot exceed 100 km or be less than 0 m.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.auth.user 

        # Extract location and hazard information from validated data
        lat = validated_data.pop("lat")
        lng = validated_data.pop("lng")
        hazard_type = validated_data.pop("hazard_type", None)
        hazard_data = validated_data.pop("hazard_data", {})

        # Reverse Geocoding using Nominatim
        try:
            geolocator = Nominatim(user_agent="enviroalerts")
            location = geolocator.reverse((lat, lng), language="en")
            address = location.raw.get("address", {}) if location else {}
        except Exception as e:
            raise serializers.ValidationError({"geocoding": f"Geocoding failed: {str(e)}"})

        # Process hazard data (remove empty strings)
        hazard_data = {
            key: (value if not (isinstance(value, str) and value.strip() == "") else None)
            for key, value in hazard_data.items()
        }

        content_type = None
        object_id = None
        hazard_instance = None

        # Create hazard instance if hazard_type is provided
        if hazard_type:
            model_class = HAZARD_MODEL_MAPPING.get(hazard_type.lower())
            if not model_class:
                raise serializers.ValidationError({"hazard_type": "Invalid hazard type."})
            try:
                hazard_instance = model_class.objects.create(**hazard_data)
                content_type = ContentType.objects.get_for_model(hazard_instance)
                object_id = hazard_instance.id
            except Exception as e:
                raise serializers.ValidationError({"hazard_data": f"Error creating Hazard: {str(e)}"})

        # Create the Alert record using the gathered information
        alert = Alert.objects.create(
            description=validated_data.get("description", ""),
            location=Point(float(lng), float(lat)),
            effect_radius=validated_data.get("effect_radius"),
            reported_by=user,
            source_url=validated_data.get("source_url"),
            country=address.get("country", ""),
            city=address.get("city", address.get("town", "")),
            county=address.get("county", ""),
            content_type=content_type,
            object_id=object_id,
        )
        return alert
