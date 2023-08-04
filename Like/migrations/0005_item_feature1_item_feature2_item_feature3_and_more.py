# Generated by Django 4.2 on 2023-08-03 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Like', '0004_alter_item_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='feature1',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='feature2',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='feature3',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='offerbody1',
            field=models.TextField(default='none'),
        ),
        migrations.AddField(
            model_name='item',
            name='offerbody2',
            field=models.TextField(default='none'),
        ),
        migrations.AddField(
            model_name='item',
            name='offerbody3',
            field=models.TextField(default='none'),
        ),
        migrations.AddField(
            model_name='item',
            name='offerhead1',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='offerhead2',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='offerhead3',
            field=models.CharField(default='none', max_length=300),
        ),
    ]
