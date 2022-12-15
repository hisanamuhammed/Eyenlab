# Generated by Django 4.1.2 on 2022-12-07 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_code', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('minimum_amount', models.IntegerField(default=999)),
                ('discount_price', models.IntegerField(default=199)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modify_date', models.DateTimeField(auto_now=True)),
                ('expiry_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='coupon_discount',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.coupon'),
        ),
    ]
