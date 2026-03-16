from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_section, name='upload'),
    path('<slug:category_slug>/', views.category_view, name='category'),
    path('<slug:category_slug>/<slug:work_slug>/', views.work_view, name='work'),
    path(
        '<slug:category_slug>/<slug:work_slug>/<slug:section_slug>/',
        views.section_view,
        name='section',
    ),
]
