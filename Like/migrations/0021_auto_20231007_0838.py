# Generated by Django 3.2.20 on 2023-10-07 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Like', '0020_auto_20230825_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='boutique_request',
            name='no_image',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='brand_banner',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='brand_logo',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='products_image1',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='products_image2',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='products_image3',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='boutique_request',
            name='products_image4',
            field=models.ImageField(blank=True, default='/static/images/banner3.png', null=True, upload_to=''),
        ),
    ]
