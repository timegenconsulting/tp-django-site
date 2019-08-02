# Generated by Django 2.1 on 2018-12-19 07:48

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orgs', '0004_organization_requests_no'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EventHook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urls', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), size=None)),
                ('emails', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=500)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('body', django.contrib.postgres.fields.jsonb.JSONField()),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='eventhook',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_url', to='events.Events'),
        ),
        migrations.AddField(
            model_name='eventhook',
            name='org',
            field=models.ManyToManyField(related_name='organization', to='orgs.Organization'),
        ),
    ]
