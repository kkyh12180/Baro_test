# Generated by Django 4.1.10 on 2023-08-14 05:23

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
            name='ChannelPost',
            fields=[
                ('channel_post_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('post_time', models.DateTimeField(auto_now_add=True)),
                ('like_number', models.IntegerField(default=0)),
                ('subscribe_only', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_post', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'channel_post',
            },
        ),
        migrations.CreateModel(
            name='ChannelPostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_like_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_post_like', to='channel.channelpost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_post_like', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'channel_post_like',
            },
        ),
    ]
