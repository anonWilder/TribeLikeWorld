# Generated by Django 4.2 on 2023-08-04 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Like', '0017_contactmessageentry_delete_contactmessage'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ContactMessageEntry',
            new_name='ContactMessage',
        ),
    ]
