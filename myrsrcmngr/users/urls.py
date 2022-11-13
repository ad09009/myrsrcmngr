from django.urls import path
from . import views

app_name='users'
urlpatterns = [
    path('<int:pk>/', views.ProfileDetailView.as_view(), name = 'profile-home'),
    path('<int:pk>/update', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('<int:pk>/delete', views.ProfileDeleteView.as_view(), name='profile-delete'),
]