# Generated by Django 4.2.11 on 2025-01-21 03:12

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Earthquake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('magnitude', models.DecimalField(decimal_places=2, help_text='Magnitude of the earthquake.', max_digits=4)),
                ('depth', models.DecimalField(decimal_places=2, help_text='Depth of the earthquake in kilometers.', max_digits=5)),
                ('epicenter_description', models.CharField(blank=True, help_text='Description of the epicenter.', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Fire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('affected_area', models.DecimalField(decimal_places=2, help_text='Affected area in square kilometers.', max_digits=10)),
                ('is_contained', models.BooleanField(default=False, help_text='Indicates if the fire is contained.')),
                ('cause', models.CharField(blank=True, help_text='Possible cause of the fire.', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Flood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('water_level', models.DecimalField(decimal_places=2, help_text='Water level in meters.', max_digits=5)),
                ('affected_area', models.DecimalField(decimal_places=2, help_text='Affected area in square kilometers.', max_digits=10)),
                ('is_flash_flood', models.BooleanField(default=False, help_text='Indicates if it is a flash flood.')),
            ],
        ),
        migrations.CreateModel(
            name='Storm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wind_speed', models.DecimalField(decimal_places=2, help_text='Wind speed in km/h.', max_digits=5)),
                ('rainfall', models.DecimalField(decimal_places=2, help_text='Rainfall in mm.', max_digits=5)),
                ('storm_category', models.IntegerField(blank=True, help_text='Category of the storm.', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tornado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wind_speed', models.DecimalField(decimal_places=2, help_text='Wind speed in km/h.', max_digits=5)),
                ('damage_description', models.TextField(blank=True, help_text='Description of the damage caused.', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(help_text='A brief description of the alert.')),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, help_text='2D geographic location of the alert.', srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deletion_time', models.DateTimeField(blank=True, help_text='Calculated time when this alert expires.', null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('county', models.CharField(blank=True, max_length=100, null=True)),
                ('source_url', models.URLField(blank=True, help_text='Source of information about the alert.', null=True)),
                ('positive_votes', models.PositiveIntegerField(default=0, help_text='Number of positive votes.')),
                ('negative_votes', models.PositiveIntegerField(default=0, help_text='Number of negative votes.')),
                ('hazard_type', models.CharField(choices=[('earthquake', 'Earthquake'), ('flood', 'Flood'), ('tornado', 'Tornado'), ('fire', 'Fire'), ('storm', 'Storm')], help_text='Type of hazard.', max_length=20)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
                ('reported_by', models.ForeignKey(blank=True, help_text='User who created the alert.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
