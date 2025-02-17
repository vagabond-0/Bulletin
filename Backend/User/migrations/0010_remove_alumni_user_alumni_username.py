# Generated by Django 5.1.2 on 2025-02-17 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0009_remove_alumni_likes_post_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alumni',
            name='user',
        ),
        migrations.AddField(
            model_name='alumni',
            name='username',
            field=models.CharField(default='default_username', max_length=255),
        ),
    ]
