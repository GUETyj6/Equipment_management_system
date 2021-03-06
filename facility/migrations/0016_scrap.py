# Generated by Django 3.0.5 on 2020-09-09 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('facility', '0015_auto_20190605_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scrap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scarp_time', models.DateField(auto_now=True, verbose_name='报废时间')),
                ('baofei_staff_name', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='上报人员')),
                ('facility_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facility.Facility', verbose_name='报废设备')),
            ],
        ),
    ]
