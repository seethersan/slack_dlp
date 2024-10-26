# Generated by Django 5.1.2 on 2024-10-26 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dlp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pattern",
            name="enabled",
            field=models.BooleanField(
                default=True, help_text="Whether the pattern is enabled"
            ),
        ),
    ]
