# Generated by Django 4.2 on 2023-08-03 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Like', '0005_item_feature1_item_feature2_item_feature3_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='Guaranteed_time',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='color_name',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='model_name',
            field=models.CharField(default='none', max_length=300),
        ),
        migrations.AddField(
            model_name='item',
            name='size_type',
            field=models.CharField(default='none', max_length=300),
        ),
    ]
