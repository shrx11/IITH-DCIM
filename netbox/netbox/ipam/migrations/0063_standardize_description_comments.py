# Generated by Django 4.1.2 on 2022-11-03 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0062_unique_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregate',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='asn',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='fhrpgroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='iprange',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='prefix',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='service',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vlan',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vrf',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
