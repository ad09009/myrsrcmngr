from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('scans/create', views.ScanCreateView.as_view(), name='new-scan'),
    path('scans/', views.ScansListView.as_view(), name='scans-list'),
    path('groups/', views.ResourcegroupsListView.as_view(), name='groups-list'),
    path('reports/', views.ReportsListView.as_view(), name='reports-list'),
    path('hosts/', views.HostsListView.as_view(), name='hosts-list'),
]
