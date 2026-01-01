# Generated manually to add years_of_experience field to FarmerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_add_farm_name_only'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmerprofile',
            name='years_of_experience',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
