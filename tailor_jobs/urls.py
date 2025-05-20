from django.urls import path
from . import views

app_name = 'tailor_jobs'

urlpatterns = [
    path('', views.tailor_jobs_form, name='form'),
    path('apply/', views.apply_for_job, name='apply'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
]