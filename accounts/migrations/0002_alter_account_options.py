# Generated by Django 4.1.2 on 2022-11-03 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'verbose_name': 'accounts', 'verbose_name_plural': 'accounts'},
        ),
    ]
