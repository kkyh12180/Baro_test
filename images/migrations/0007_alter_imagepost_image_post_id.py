# Generated by Django 4.1.10 on 2023-08-11 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0006_delete_imagepostlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagepost',
            name='image_post_id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]