# Generated by Django 4.2.4 on 2023-12-06 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatapp', '0008_remove_comments_anti_display'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='cluster_display',
        ),
        migrations.RemoveField(
            model_name='comments',
            name='cluster_label',
        ),
    ]
