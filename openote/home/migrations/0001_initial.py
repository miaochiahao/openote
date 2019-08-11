# Generated by Django 2.2.4 on 2019-08-09 15:38

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HTTPLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('method', models.CharField(max_length=16)),
                ('content', models.TextField()),
                ('host', models.TextField()),
                ('source', models.CharField(max_length=64)),
            ],
        ),
    ]