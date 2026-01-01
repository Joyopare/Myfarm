# Generated manually to add followers field to FarmerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20250829_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmerprofile',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='following', to='accounts.customerprofile'),
        ),
    ]
