# Generated by Django 3.2.16 on 2024-05-03 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_post_comment_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='comment_count',
            field=models.PositiveSmallIntegerField(blank=True, default=0, verbose_name='Количество комментариев'),
        ),
    ]
