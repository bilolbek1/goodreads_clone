# Generated by Django 4.2.3 on 2023-07-31 07:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_book_books_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
