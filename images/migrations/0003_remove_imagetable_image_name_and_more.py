# Generated by Django 4.1.10 on 2023-07-25 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_alter_imagepost_like_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagetable',
            name='image_name',
        ),
        migrations.AlterField(
            model_name='imagepost',
            name='image_post_id',
            field=models.CharField(max_length=11, primary_key=True, serialize=False),
        ),
    ]