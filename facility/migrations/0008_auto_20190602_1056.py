# Generated by Django 2.0 on 2019-06-02 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facility', '0007_auto_20190602_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repair',
            name='baoxiu_staff_tel',
            field=models.CharField(blank=True, max_length=11, null=True, verbose_name='联系方式'),
        ),
    ]
