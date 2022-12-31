from django.test import TestCase
from django.test import Client
from bs4 import BeautifulSoup
import json
from django.urls import reverse
from .models import scans, hosts, reports, resourcegroups, services, changes
from django.contrib.auth.models import User

# Create your tests here.


class TestScansViews(TestCase):
    
    urls_login_protected = ['new-scan','new-group','edit-scan','edit-group','delete-scan','delete-group',]
    
    urls_crud = ['index',
                'scans-list',
                
                'groups-list',
             
                'hosts-list',
                'reports-list',
                'search',]
    
    urls_api_pk = [
                'scan-progress',
                'reports-refresh',
                'scans-group-refresh',
                'groups-changes',
                'hosts-refresh',
                'host-changes',
                'host-services',
               ]
    
    urls_api = [
                'dashboard-changes',
                'changes-only',
                'dashboard-scans',
                'scans-refresh',
                'scans-totals',
                'groups-refresh',
                'groups-totals',
                'hosts-totals',
                'hosts-all-refresh',
                'reports-totals',
                'reports-all-refresh',]

    urls_crud_pk = ['scan-detail',
                    'edit-scan',
                    'delete-scan',
                    'groups-detail',
                    'edit-group',
                    'delete-group',
                    'hosts-detail',
                    'edit-host',
                    'report-detail',
                    'download_report',
                    'service-detail',]

    urls_search = ['search',]

    urls_charts = ['groups-chart',
                    'scans-chart',
                    'hosts-chart',
                    'reports-chart',
                    'dashboard-chart',]
    
    def test_scan_saving(self):
        # Create a test user
        test_user = User.objects.create_user(
            username='testuser', password='314LABsa'
        )
        # Create a test group
        test_group = resourcegroups.objects.create(
            name='testgroup',
            description='Test group for unit testing',
            subnet='192.168.16.0/24'
        )
        # Create a test scan
        test_scan = scans.objects.create(
            scanAuthor=test_user,
            resourcegroup=test_group,
            ScanTemplate='-vvv --stats-every 1s --top-ports 100 -T2',
            ScanSchedule='hh',
            active=False
        )
        # Check that the scan was saved correctly
        saved_scan = scans.objects.get(id=test_scan.id)
        self.assertEqual(saved_scan.scanAuthor, test_user)
        self.assertEqual(saved_scan.resourcegroup, test_group)
        self.assertEqual(saved_scan.ScanTemplate, '-vvv --stats-every 1s --top-ports 100 -T2')
        self.assertFalse(saved_scan.active)
        
    
    def test_scans_list_view(self):
        # Create a client
        client = Client()

        # Send a GET request to the view
        response = client.get('/scans/')
        scancount = scans.objects.all().count()
        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the rendered context contains the expected data
        self.assertIn('scans_list', response.context)
        self.assertEqual(len(response.context['scans_list']), scancount)

    def test_all_links_reachable_main(self, url=None):
        # Create a client instance
        client = Client()
        if not url:
            url = reverse('website:index')
        else:
            url = reverse('website:'+url)
        # Crawl the entire website
        response = client.get(url)
        #print('first call: ', url)
        self.assertEqual(response.status_code, 200)

        # Find all anchor tags in the website
        soup = BeautifulSoup(response.content, 'html.parser')
        anchors = soup.find_all('a')

        # Check if each anchor tag's href is reachable
        for anchor in anchors:
            href = anchor['href']
            response = client.get(href)
            #print(href)
            self.assertEqual(response.status_code, 200)
    
    def test_crudlinks_reachable(self):
        for url in self.urls_crud:
            response = self.client.get(reverse('website:'+url))
            self.assertEqual(response.status_code, 200)
    
    def test_apilinks_reachable(self):
        for url in self.urls_api:
            response = self.client.get(reverse('website:'+url))
            self.assertEqual(response.status_code, 200)
    
    def test_crudlinks_a_tags_reachable(self):
        for url in self.urls_crud:
            #print('second call: ', url)
            self.test_all_links_reachable_main(url)
          
    def test_ajax_view(self):
        # Send an AJAX request to the view
        response = self.client.get(reverse('website:dashboard-changes'))
        
        # Assert that the response has a 200 status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Assert that the JSON response is as expected
        self.assertEqual(data['data']['total'], len(data['data']['changes']))
        
    def test_api_post_view(self):
        # Set up the client and request data
        client = Client()

        test_user = User.objects.create_user(
            username='testuser7', password='314LABsa'
        )
        # Create a test group
        test_group = resourcegroups.objects.create(
            name='testgroup3',
            description='Test group for unit testing',
            subnet='192.168.20.0/24'
        )
        # Create a test scan
        test_scan = scans.objects.create(
            scanAuthor=test_user,
            resourcegroup=test_group,
            ScanTemplate='-vvv --stats-every 1s --top-ports 100 -T2',
            ScanSchedule='hh',
            active=False
        )
        # Check that the scan was saved correctly
        saved_scan = scans.objects.get(id=test_scan.id)
        self.assertEqual(saved_scan.scanAuthor, test_user)
        self.assertEqual(saved_scan.resourcegroup, test_group)
        self.assertEqual(saved_scan.ScanTemplate, '-vvv --stats-every 1s --top-ports 100 -T2')
        self.assertFalse(saved_scan.active)

        #Create report
        test_report = reports.objects.create(
            scan=test_scan,
            resourcegroup=test_group,
            standard=False,
            summary='Test report for unit testing',
        )
        saved_report = reports.objects.get(id=test_report.id)
        self.assertEqual(saved_report.scan, test_scan)
        self.assertEqual(saved_report.resourcegroup, test_group)
        self.assertEqual(saved_report.summary, 'Test report for unit testing')
        self.assertFalse(saved_report.standard)

        dismiss_url = reverse('website:dashboard-dismiss')
        response = client.post(dismiss_url, {}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'dismissed': True})
        
        toggle_url = reverse('website:scan-toggle', args=[test_scan.id])
        toggle_data = {'active': 1}
        response = client.post(toggle_url, toggle_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'active': None})
        
        #standard_data = {'standard': 1}
        #standard_url = reverse('website:set-standard-report', args=[test_report.id])
        #response = client.post(standard_url, standard_data, content_type='application/json')
        #self.assertEqual(response.status_code, 200)
        #response_data = json.loads(response.content)
        #self.assertEqual(response_data, {'standard': 1})    
