# Generated by Django 4.0.4 on 2022-05-02 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_ingridient'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Ingridient',
            new_name='Ingredient',
        ),
    ]
