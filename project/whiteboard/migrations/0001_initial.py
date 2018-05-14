# Generated by Django 2.0.5 on 2018-05-14 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('genesis', models.DateField()),
                ('updated', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('username', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('password_hash', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='whiteboard.User'),
        ),
    ]
