from django.shortcuts import render
from django.views import generic
from .models import Survey


# define the index request (wss/)
def index(request):
    return render(request, 'wss/index.html')


# define the survey detail view
class SurveyDetailView(generic.DetailView):
    model = Survey
    template_name = 'wss/survey_detail.html'
