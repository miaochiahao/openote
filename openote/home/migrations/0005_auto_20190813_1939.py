# Generated by Django 2.2.4 on 2019-08-13 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_fileservice_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileservice',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
