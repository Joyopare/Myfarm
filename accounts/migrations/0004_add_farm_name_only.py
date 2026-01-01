# Generated manually to add only farm_name field to FarmerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_add_followers_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmerprofile',
            name='farm_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='farmerprofile',
            name='farm_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='farmerprofile',
            name='farming_methods',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
