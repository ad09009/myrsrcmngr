# MyRsrcMngr

The project consists of a [Django](https://www.djangoproject.com/) web application that allows users to execute  [NMAP](https://nmap.org) scans on a given target (single IP address, subnet, list of IP addresses), save the scan results, compare them to previous scans and view a summary of the differences. It also allows users to create, view and manage their scans, hosts and groups (of hosts or resources).

The application is developed in Django 4.1.3 and utilizes the [libnmap](https://libnmap.readthedocs.io/en/latest/) library for calling NMAP, managing the calls and parsing the generated reports. The [APScheduler](https://apscheduler.readthedocs.io/en/3.x/) library is used for scheduling scan executions.

The application features a dashboard that displays live updates on observed changes (host status changes, new open ports, os fingerprint changes) and active scan statuses. Charts to visualize the collected data are implemented with the [Charts.js](https://github.com/chartjs/awesome) library for Django ([django-chartjs](https://github.com/peopledoc/django-chartjs)). Data is represented in tables powered by the [DataTables](https://datatables.net/)library that include sorting, searching and pagination. The main template is a modified implementation of the SB Admin template (v7.0.5) by [startbootstrap](https://startbootstrap.com/template/sb-admin). [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/) is used elsewhere for styling too, [jQuery](https://jquery.com/) for AJAX calls, [Django REST Framework](https://www.django-rest-framework.org) is used to build API views, [django-crispy-forms](https://django-crispy-forms.readthedocs.io/en/latest/) library is used to style forms. User management is handled by Django's built-in authentication system with slight modifications. 


## Requirements

The project was developed on:
- Ubuntu 22.04.1
- Python 3.10.6
- Nmap 7.80

The chosen database solutions (but other options compatible with Django should work just as well):
- sqlite3 3.37.2 (normally should already be included)
- MariaDB 15.1


## Installation

To install the project and its dependencies, first create and activate a dedicated virtual environment to work in and then follow these steps:

#### 1. Clone this repository:
   `$ git clone https://...`

#### 1. Install the non-pip requirements (the following command should do the trick as Python and sqlite3 should already be included):
   `$ sudo apt install nmap `

#### 2. Install the necessary python packages from the requirements file:
   `$ pip install -r requirements.txt`

#### 3. Set up the database (the default sqlite one):
   `$ python manage.py makemigrations`
   `$ python manage.py migrate`

#### 3. Create a superuser:
   `$ python manage.py createsuperuser`

#### 4. Run the project (with --noreload option to avoid conflicts due to the way scheduling is implemented and Django dev server operates):
   `$ python manage.py runserver --noreload`


## Use case

#### 1. Register and/or log in
#### 2. Go to Groups, click on Options and Create New Group.
#### 3. Enter Group name, description (optionally) and the target subnet (in CIDR notation) or IPv4 addresses (comma separated list) and click Save.
#### 4. Navigate to Scans, click on Options and Create New Scan.
#### 5. Choose the previously created Group, enter a name for the Scan, choose Nmap options to run from template list and choose a schedule for the Scan, then press Save.
#### 6. Find the newly created Scan, open it, click on Options and click "Turn On". Your scan should start execution in a few seconds, you will see the status in the Status panel.
#### 7. When scan execution finishes, the generated report will be listed in a table under the scan.
#### 8. You can navigate to the report, click on Options and Download Report to save the full xml file.
#### 9. Or study the results in other views of the web app, like the Dashboard.
#### 10. Now that you have one report done, every next Nmap report for this scan will be able to provide a comparison, noting important changes which are displayed on the Dashboard, in the report detail view and on host detail view as well.
#### 11. Be default each new report is compared to the previous report for this scan. This can be changed to a permanent Standard report to compare to - choose a report, click on Options and Set as Standard to do that.


## Limitations

- Only non-sudo options for Nmap are supported (new ones should be added to the "scans" model)
- Only one active scan per Group at a time is currently supported.


## Troubleshooting

- Logs for the execution of scheduled Nmap scans (and report parsing) are stored in 'scanrunner.log' file.
- Libnmap logs of Nmap execution are stored in /logs .
- Django logs print out to standard output.


## Security warning:

Make sure to deploy this **ONLY** locally as it is not secured.


## Legal warning:

Keep in mind that like other network probing or port scanning tools Nmap should generally be used **only** when explicit authorization by target host or network exists.
[Read this page](https://nmap.org/book/legal-issues.html) on legal issues related to Nmap use.