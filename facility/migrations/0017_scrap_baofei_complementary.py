# Generated by Django 3.0.5 on 2020-09-09 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facility', '0016_scrap'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrap',
            name='baofei_complementary',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='报废描述'),
        ),
    ]