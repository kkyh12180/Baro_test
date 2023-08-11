# Generated by Django 4.1.10 on 2023-08-11 06:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImagePost',
            fields=[
                ('image_post_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('thumbnail_image', models.TextField()),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('like_number', models.IntegerField(default=0)),
                ('adult', models.BooleanField(default=False)),
                ('subscribe_only', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_post', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'image_post',
            },
        ),
        migrations.CreateModel(
            name='ImageTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_id', models.CharField(max_length=10, unique=True)),
                ('image_file', models.TextField()),
                ('seed', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('steps', models.IntegerField(blank=True, default=None, null=True)),
                ('sampler', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('cfg_scale', models.FloatField(blank=True, default=None, null=True)),
                ('model_hash', models.CharField(blank=True, default=None, max_length=30, null=True)),
                ('clip_skip', models.IntegerField(blank=True, default=None, null=True)),
                ('denoising_strength', models.FloatField(blank=True, default=None, null=True)),
                ('image_time', models.DateTimeField(auto_now_add=True)),
                ('adult', models.BooleanField(default=False)),
                ('image_post_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='images.imagepost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'image_table',
                'unique_together': {('image_id', 'image_post_id')},
            },
        ),
        migrations.CreateModel(
            name='ImagePrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('is_positive', models.BooleanField(null=True)),
                ('prompt_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('image', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prompt', to='images.imagetable')),
            ],
            options={
                'db_table': 'image_prompt',
            },
        ),
    ]
