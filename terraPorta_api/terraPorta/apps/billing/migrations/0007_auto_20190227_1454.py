# Generated by Django 2.1 on 2019-02-27 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_billingplan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='org',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orgs.Organization'),
        ),
    ]
