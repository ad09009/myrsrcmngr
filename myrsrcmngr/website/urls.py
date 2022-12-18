from django.urls import path
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('scans/create', views.ScanCreateView.as_view(), name='new-scan'),
    path('scans/', views.ScansListView.as_view(), name='scans-list'),
    #Scans list JSON response
    path('scans/json/', views.scans_list),
    path('groups/', views.ResourcegroupsListView.as_view(), name='groups-list'),
    path('groups/<int:pk>/', views.ResourcegroupDetailView.as_view(), name='groups-detail'),
    path('scans/<int:pk>/', views.ScanDetailView.as_view(), name='scan-detail'),
    path('scans/api/<int:pk>/', views.ScanProgressView.as_view(), name='scan-progress'),
    path('scans/api/toggle/<int:pk>/', views.scan_toggle, name='scan-toggle'),
    path('reports/', views.ReportsListView.as_view(), name='reports-list'),
    path('hosts/', views.HostsListView.as_view(), name='hosts-list'),
    
    path('search/', views.GlobalSearch, name='search'),
    path('hosts/<int:pk>/', views.HostDetailView.as_view(), name='hosts-detail'),
]
