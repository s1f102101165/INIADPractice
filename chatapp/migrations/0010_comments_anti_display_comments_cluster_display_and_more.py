from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatapp', '0009_remove_comments_cluster_display_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='anti_display',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comments',
            name='cluster_display',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comments',
            name='cluster_label',
            field=models.IntegerField(default=-1),
        ),

    ]
