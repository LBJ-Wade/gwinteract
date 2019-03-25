from django.conf.urls import url

from . import views

app_name = 'hubble_constant'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^hubble-constant/$', views.hubble_constant, name='hubble_constant'),
    url(r'^plot/$', views.plot_ho, name='plot'),
    url(r'^json/$', views.ho_json, name='json'),
]
