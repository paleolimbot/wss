from django.conf.urls import url
from . import views

app_name = 'wss'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^take/(?P<pk>[0-9]+)/$', views.SurveyDetailView.as_view(), name='survey'),
]
