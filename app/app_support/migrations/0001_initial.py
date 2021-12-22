# Generated by Django 4.0 on 2021-12-16 00:15

import app_support.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_support', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now_add=True)),
                ('hide_private_info', models.BooleanField(default=False)),
                ('screen_name', models.CharField(blank=True, max_length=250)),
                ('personal_information', models.TextField(blank=True, max_length=2000)),
                ('opened_tickets_count', models.IntegerField(default=0)),
                ('last_answer_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_theme', models.CharField(choices=[('1', 'product'), ('2', 'soft'), ('3', 'security'), ('4', 'other')], max_length=255)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('last_update', models.DateTimeField(auto_now_add=True)),
                ('last_support_answer', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_closed', models.BooleanField(default=False)),
                ('was_closed_by', models.CharField(blank=True, max_length=250)),
                ('is_frozen', models.BooleanField(default=False)),
                ('staff_note', models.TextField(blank=True, default='', max_length=10000)),
                ('answered', models.BooleanField(default=True)),
                ('opened_by', models.ForeignKey(on_delete=models.SET(app_support.models.get_current_tc_user_object), related_name='tickets', related_query_name='ticket', to='app_support.appuser')),
            ],
            options={
                'ordering': ['id', 'last_support_answer', 'creation_date', 'is_closed', 'answered'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(default='', max_length=1000)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('linked_ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', related_query_name='message', to='app_support.ticket')),
                ('linked_user', models.ForeignKey(on_delete=models.SET(app_support.models.get_current_tc_user_object), to='app_support.appuser')),
            ],
        ),
    ]