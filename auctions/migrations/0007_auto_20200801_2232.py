# Generated by Django 3.0.8 on 2020-08-01 22:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20200801_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='watchers',
            field=models.ManyToManyField(blank=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
