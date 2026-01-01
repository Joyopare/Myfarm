# Generated manually to remove conflicting fields that are now properties

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_years_of_experience'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farmerprofile',
            name='total_sales',
        ),
        migrations.RemoveField(
            model_name='farmerprofile',
            name='average_rating',
        ),
        migrations.RemoveField(
            model_name='farmerprofile',
            name='total_followers',
        ),
    ]
