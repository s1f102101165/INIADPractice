# Generated by Django 4.2.4 on 2023-12-20 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatapp', '0012_rename_anti_label_comments_anti_violence_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='useOpenAIAPI',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='comments',
            name='anti_display',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='comments',
            name='cluster_display',
            field=models.IntegerField(default=0),
        ),
    ]