# Generated by Django 2.1 on 2019-02-25 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_payment_org'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.IntegerField()),
                ('description', models.CharField(default='One month', max_length=250)),
                ('price', models.FloatField(default=0)),
            ],
        ),
    ]
