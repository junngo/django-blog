# Generated by Django 3.1.7 on 2021-04-07 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_file_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hook_text',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
