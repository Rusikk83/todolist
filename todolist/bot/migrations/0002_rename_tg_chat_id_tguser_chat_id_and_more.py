# Generated by Django 4.0.1 on 2023-06-23 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tguser',
            old_name='tg_chat_id',
            new_name='chat_id',
        ),
        migrations.RenameField(
            model_name='tguser',
            old_name='tg_user',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='tguser',
            old_name='tg_verification_code',
            new_name='verification_code',
        ),
    ]