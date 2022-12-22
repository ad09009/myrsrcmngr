from django.urls import path, reverse_lazy
from . import views

app_name = 'website'
urlpatterns = [
    path('', views.dashboard, name='index'),
    path('about', views.about, name='about'),
    
    #Scans list JSON response
    path('scans/json/', views.scans_list),
    path('scans/', views.ScansListView.as_view(), name='scans-list'),
    path('scans/create', views.ScanCreateView.as_view(), name='new-scan'),
    path('scans/<int:pk>', views.ScanDetailView.as_view(), name='scan-detail'),
    path('scans/<int:pk>/edit', views.ScanUpdateView.as_view(), name='edit-scan'),
    path('scans/<int:pk>/delete', views.ScanDeleteView.as_view(success_url=reverse_lazy('website:index')), name='delete-scan'),
    path('scans/api/<int:pk>/', views.ScanProgressView.as_view(), name='scan-progress'),
    path('scans/api/toggle/<int:pk>/', views.scan_toggle, name='scan-toggle'),
    path('scans/api/refresh/scans/<int:pk>/', views.scan_refresh, name='reports-refresh'),
    path('scans/api/refresh/scans/', views.scanlist_refresh, name='scans-refresh'),
    path('groups/api/refresh/groups/', views.grouplist_refresh, name='groups-refresh'),
    path('groups/', views.ResourcegroupsListView.as_view(), name='groups-list'),
    path('groups/<int:pk>/', views.ResourcegroupDetailView.as_view(), name='groups-detail'),
    path('groups/create', views.ResourcegroupCreateView.as_view(), name='new-group'),
    path('groups/<int:pk>/edit', views.ResourcegroupUpdateView.as_view(), name='edit-group'),
    path('groups/<int:pk>/delete', views.ResourcegroupDeleteView.as_view(success_url=reverse_lazy('website:index')), name='delete-group'),

    path('scans/api/refresh/totals/', views.scanlist_totals_refresh, name='scans-totals'),
    path('groups/api/refresh/totals/', views.grouplist_totals_refresh, name='groups-totals'),
    path('groups/api/refresh/changes/<int:pk>/', views.group_changes_refresh, name='groups-changes'),
    path('reports/', views.ReportsListView.as_view(), name='reports-list'),
    path('reports/<int:pk>', views.ReportDetailView.as_view(), name='report-detail'),
    path('hosts/', views.HostsListView.as_view(), name='hosts-list'),
    path('hosts/<int:pk>/', views.HostDetailView.as_view(), name='hosts-detail'),
    path('groups/api/refresh/hosts/', views.hostsgroup_refresh, name='hosts-refresh'),
    path('search/', views.GlobalSearch, name='search'),
]
