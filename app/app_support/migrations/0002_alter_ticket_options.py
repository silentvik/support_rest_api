# Generated by Django 4.0 on 2021-12-14 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_support', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['id', 'last_support_answer', 'creation_date', 'is_closed', 'answered']},
        ),
    ]
