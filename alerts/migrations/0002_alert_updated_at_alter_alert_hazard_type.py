# Generated by Django 4.2.11 on 2025-01-23 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='alert',
            name='hazard_type',
            field=models.CharField(choices=[('earthquake', 'Earthquake'), ('flood', 'Flood'), ('tornado', 'Tornado'), ('fire', 'Fire'), ('storm', 'Storm')], db_index=True, help_text='Type of hazard.', max_length=20),
        ),
    ]
