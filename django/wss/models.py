from django.db import models


# these models define the surveys, sections, questions, and choices
class Survey(models.Model):
    title = models.CharField(max_length=200)
    detail = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Section(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    detail = models.TextField(blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    survey_section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    question_detail = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    choice_detail = models.CharField(max_length=200, blank=True)
    score = models.IntegerField(default=None, blank=True, null=True)
    report_text = models.CharField(max_length=200, default=None, blank=True)
    next_question = models.ForeignKey(Question, on_delete=models.SET_NULL,
                                      related_name='next', default=None, blank=True,
                                      null=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.choice_text


# these models define the user responses
class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    started = models.DateTimeField(auto_now=True)
    ended = models.DateTimeField(blank=True, )

    def __str__(self):
        return 'Response to "%s" by "%s"' % (self.survey, self.user)


class QuestionResponse(models.Model):
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE)
    survey_question = models.ForeignKey(Question, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    survey_choice = models.ForeignKey(Choice, on_delete=models.PROTECT, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return '%s <%s>' % (self.survey_choice, self.comments)
