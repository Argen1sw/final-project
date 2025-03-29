import factory
import random

from django.utils.timezone import now
from datetime import timedelta
from django.contrib.gis.geos import Point
from django.contrib.contenttypes.models import ContentType

from users.models import User
from alerts.models import (Alert, Earthquake, Flood,
                           Tornado, Fire)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    is_suspended = False
    alerts_upvoted = 0

class EarthquakeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Earthquake

    magnitude = 5.5
    depth = 10.0
    epicenter_description = factory.Faker('sentence')

class FloodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Flood

    severity = factory.Iterator(['low', 'moderate', 'major'])
    water_level = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    is_flash_flood = factory.Faker('pybool')

class TornadoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tornado

    category = factory.Iterator(['EF0', 'EF1', 'EF2', 'EF3', 'EF4', 'EF5'])
    damage_description = factory.Faker('sentence')

class FireFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fire

    fire_intensity = factory.Iterator(['low', 'moderate', 'high'])
    is_contained = factory.Faker('pybool')
    cause = factory.Faker('sentence')

class AlertFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Alert
        # Exclude the transient attribute so it isn't passed to the model's constructor.
        exclude = ('hazard_instance',)

    # Transient attribute that holds the hazard instance.
    hazard_instance = factory.LazyFunction(
        lambda: random.choice([
            EarthquakeFactory(),
            FloodFactory(),
            TornadoFactory(),
            FireFactory()
        ])
    )

    description = factory.Faker('sentence')
    location = factory.LazyFunction(lambda: Point(0, 0))
    effect_radius = 10000
    country = "Testland"
    city = "Testcity"
    reported_by = factory.SubFactory(UserFactory)
    is_active = True
    soft_deletion_time = factory.LazyFunction(lambda: now() + timedelta(days=2))
    
    # Use the transient hazard_instance to set content_type and object_id.
    content_type = factory.LazyAttribute(lambda a: ContentType.objects.get_for_model(a.hazard_instance))
    object_id = factory.LazyAttribute(lambda a: a.hazard_instance.id)