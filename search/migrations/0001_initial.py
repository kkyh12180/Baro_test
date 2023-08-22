# Generated by Django 4.1.10 on 2023-08-22 05:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('prompt', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('positive_weight', models.IntegerField(default=0)),
                ('negative_weight', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'prompt',
            },
        ),
        migrations.CreateModel(
            name='Prompt_log',
            fields=[
                ('prompt_log_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('prompt', models.TextField()),
                ('negative_prompt', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prompt_log', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'prompt_log',
            },
        ),
    ]
