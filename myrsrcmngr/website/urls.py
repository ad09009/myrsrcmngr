from django.urls import path, reverse_lazy
from . import views

app_name = 'website'
urlpatterns = [
    #Dashboard
    path('', views.dashboard, name='index'),
    
    #Dashboard API for AJAX calls
    path('dashboard/api/dismissed/', views.dashboard_dismiss, name='dashboard-dismiss'),
    path('dashboard/api/changes/', views.dashboard_changes, name='dashboard-changes'),
    path('changes/', views.dashboard_changes_table, name='changes-only'),
    
    #Scans CRUD
    path('scans/', views.ScansListView.as_view(), name='scans-list'),
    path('scans/create', views.ScanCreateView.as_view(), name='new-scan'),
    path('scans/<int:pk>', views.ScanDetailView.as_view(), name='scan-detail'),
    path('scans/<int:pk>/edit', views.ScanUpdateView.as_view(), name='edit-scan'),
    path('scans/<int:pk>/delete', views.ScanDeleteView.as_view(success_url=reverse_lazy('website:scans-list')), name='delete-scan'),
    
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
    path('groups/<int:pk>/delete', views.ResourcegroupDeleteView.as_view(success_url=reverse_lazy('website:groups-list')), name='delete-group'),
    
    #Resource groups API for AJAX calls
    path('groups/api/refresh/groups/', views.grouplist_refresh, name='groups-refresh'),
    path('groups/api/refresh/scans/<int:pk>/', views.scans_group_refresh, name='scans-group-refresh'),
    path('groups/api/refresh/totals/', views.grouplist_totals_refresh, name='groups-totals'),
    path('groups/api/refresh/changes/<int:pk>/', views.group_changes_refresh, name='groups-changes'),
    path('groups/api/refresh/hosts/<int:pk>/', views.hostsgroup_refresh, name='hosts-refresh'),

    #Hosts CRUD
    path('hosts/', views.HostsListView.as_view(), name='hosts-list'),
    path('hosts/<int:pk>/', views.HostDetailView.as_view(), name='hosts-detail'),
    path('hosts/<int:pk>/edit', views.HostUpdateView.as_view(), name='edit-host'),
    
    #Hosts API for AJAX calls
    path('hosts/api/refresh/totals/', views.hosts_totals_refresh, name='hosts-totals'),
    path('hosts/api/refresh/hosts/', views.hosts_refresh, name='hosts-all-refresh'),
    path('hosts/api/refresh/changes/<int:pk>/', views.host_changes_refresh, name='host-changes'),
    path('hosts/api/refresh/services/<int:pk>/', views.host_services_refresh, name='host-services'),
    
    #Reports CRUD
    path('reports/', views.ReportsListView.as_view(), name='reports-list'),
    path('reports/<int:pk>', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/download/', views.download_report, name='download_report'),
    
    #Reports API for AJAX calls 
    path('reports/api/toggle/<int:pk>/', views.set_standard_report, name='set-standard-report'),
    path('reports/api/refresh/totals/', views.reports_totals_refresh, name='reports-totals'),
    path('reports/api/refresh/reports/', views.reports_refresh, name='reports-all-refresh'),
    
    #Services CRUD
    path('services/<int:pk>', views.ServiceDetailView.as_view(), name='service-detail'),
    
    #Services API for AJAX calls
    
    
    #Search
    path('search/', views.GlobalSearch, name='search'),
    
    #Scans list JSON response
    path('scans/json/', views.scans_list),
    
    #Chart refresh API
    path('groups/api/chart/', views.groups_piechart, name='groups-chart'),
    path('scans/api/chart/', views.scans_chart, name='scans-chart'),
    path('hosts/api/chart/', views.hosts_chart, name='hosts-chart'),
    path('reports/api/chart/', views.reports_chart, name='reports-chart'),
    path('dashboard/api/chart/', views.dashboard_chart, name='dashboard-chart'),
]
