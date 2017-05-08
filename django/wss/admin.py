from django.contrib import admin
import nested_admin

from .models import Survey, Section, Question, Choice, SurveyResponse, QuestionResponse


class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 1
    fk_name = 'question'


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [ChoiceInline, ]
    extra = 1


class SurveySectionInline(nested_admin.NestedStackedInline):
    model = Section
    inlines = [QuestionInline, ]
    extra = 0


class SurveyAdmin(nested_admin.NestedModelAdmin):
    model = Survey
    inlines = [SurveySectionInline, ]


admin.site.register(Survey, SurveyAdmin)
