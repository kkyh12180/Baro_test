# Generated by Django 4.1.10 on 2023-08-22 05:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('posts', '0001_initial'),
        ('images', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('content', models.TextField(blank=True)),
                ('comment_time', models.DateTimeField(auto_now_add=True)),
                ('like_number', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'comment',
            },
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comment', to='comments.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_comment', to='posts.post')),
            ],
            options={
                'db_table': 'post_comment',
            },
        ),
        migrations.CreateModel(
            name='ImageComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_comment', to='comments.comment')),
                ('image_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_comment', to='images.imagepost')),
            ],
            options={
                'db_table': 'image_comment',
            },
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_like_time', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like', to='comments.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'comment_like',
            },
        ),
        migrations.CreateModel(
            name='ChannelPostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_comment', to='channel.channelpost')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='channel_comment', to='comments.comment')),
            ],
            options={
                'db_table': 'channel_post_comment',
            },
        ),
    ]
