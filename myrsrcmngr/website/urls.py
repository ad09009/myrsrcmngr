from django.urls import path, reverse_lazy
from . import views

app_name = 'website'
urlpatterns = [
    #Dashboard
    path('', views.dashboard, name='index'),
    
    #Scans CRUD
    path('scans/', views.ScansListView.as_view(), name='scans-list'),
    path('scans/create', views.ScanCreateView.as_view(), name='new-scan'),
    path('scans/<int:pk>', views.ScanDetailView.as_view(), name='scan-detail'),
    path('scans/<int:pk>/edit', views.ScanUpdateView.as_view(), name='edit-scan'),
    path('scans/<int:pk>/delete', views.ScanDeleteView.as_view(success_url=reverse_lazy('website:index')), name='delete-scan'),
    
    #Scans API for AJAX calls
    path('scans/api/<int:pk>/', views.ScanProgressView.as_view(), name='scan-progress'),
    path('scans/api/toggle/<int:pk>/', views.scan_toggle, name='scan-toggle'),
    path('scans/api/refresh/scans/<int:pk>/', views.scan_refresh, name='reports-refresh'),
    path('scans/api/refresh/scans/', views.scanlist_refresh, name='scans-refresh'),
    path('scans/api/refresh/totals/', views.scanlist_totals_refresh, name='scans-totals'),

    #Resource groups CRUD
    path('groups/', views.ResourcegroupsListView.as_view(), name='groups-list'),
    path('groups/create', views.ResourcegroupCreateView.as_view(), name='new-group'),
    path('groups/<int:pk>/', views.ResourcegroupDetailView.as_view(), name='groups-detail'),
    path('groups/<int:pk>/edit', views.ResourcegroupUpdateView.as_view(), name='edit-group'),
    path('groups/<int:pk>/delete', views.ResourcegroupDeleteView.as_view(success_url=reverse_lazy('website:index')), name='delete-group'),
    
    #Resource groups API for AJAX calls
    path('groups/api/refresh/groups/', views.grouplist_refresh, name='groups-refresh'),
    path('groups/api/refresh/scans/<int:pk>/', views.scans_group_refresh, name='scans-group-refresh'),
    path('groups/api/refresh/totals/', views.grouplist_totals_refresh, name='groups-totals'),
    path('groups/api/refresh/changes/<int:pk>/', views.group_changes_refresh, name='groups-changes'),
    path('groups/api/refresh/hosts/<int:pk>/', views.hostsgroup_refresh, name='hosts-refresh'),
    path('groups/api/refresh/hosts/<int:pk>/', views.hostsgroup_refresh, name='hosts-refresh'),

    #Hosts CRUD
    path('hosts/', views.HostsListView.as_view(), name='hosts-list'),
    path('hosts/<int:pk>/', views.HostDetailView.as_view(), name='hosts-detail'),
    
    #Hosts API for AJAX calls
    
    
    #Reports CRUD
    path('reports/', views.ReportsListView.as_view(), name='reports-list'),
    path('reports/<int:pk>', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/download/', views.download_report, name='download_report'),
    
    #Reports API for AJAX calls 
    path('reports/api/toggle/<int:pk>/', views.set_standard_report, name='set-standard-report'),
    
    #Services CRUD
    
    
    #Services API for AJAX calls
    
    
    #Search
    path('search/', views.GlobalSearch, name='search'),
    
    #Scans list JSON response
    path('scans/json/', views.scans_list),
]
