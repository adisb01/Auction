# Generated by Django 3.0.8 on 2020-07-30 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_bid_comment_listing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('OT', 'Other'), ('FS', 'Fashion'), ('TY', 'Toys'), ('HM', 'Home'), ('PD', 'Productivity'), ('TG', 'Technology')], default='OT', max_length=2),
        ),
    ]
