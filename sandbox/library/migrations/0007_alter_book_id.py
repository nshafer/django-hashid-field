# Generated by Django 3.2.5 on 2021-09-17 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_author_id_str'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
