# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 00:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('comments', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('detail', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=200)),
                ('choice_detail', models.CharField(blank=True, max_length=200)),
                ('score', models.IntegerField(blank=True, default=None)),
                ('report_text', models.CharField(blank=True, default=None, max_length=200)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=200)),
                ('question_detail', models.CharField(blank=True, max_length=200)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started', models.DateTimeField(auto_now=True)),
                ('ended', models.DateTimeField(blank=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wss.Survey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SurveySection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('detail', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wss.Survey')),
            ],
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='survey_section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wss.SurveySection'),
        ),
        migrations.AddField(
            model_name='surveychoice',
            name='next_question',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='next', to='wss.SurveyQuestion'),
        ),
        migrations.AddField(
            model_name='surveychoice',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wss.SurveyQuestion'),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='survey_choice',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='wss.SurveyChoice'),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='survey_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wss.SurveyQuestion'),
        ),
        migrations.AddField(
            model_name='questionresponse',
            name='survey_response',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wss.SurveyResponse'),
        ),
    ]
