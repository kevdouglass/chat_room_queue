# Generated by Django 3.0.9 on 2021-12-02 01:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0002_auto_20211125_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='users',
            field=models.ManyToManyField(related_name='rooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
