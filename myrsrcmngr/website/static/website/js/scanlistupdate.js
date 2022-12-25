function updateMsg() {
    console.log('Requesting scan JSON');
    var urlis = $("#scanprogress").attr("data-ajax-target");
    var spinner = $("#scanprogress").attr("altstuff");
    $.getJSON(urlis, function(scanreturn){
        console.log('JSON', scanreturn);

        /*Status updates*/
        /*if no scan is found by the ajax call*/
        if (scanreturn['scan'] == 0){
            $('#stable-scanprogress').empty();
            $('#scanprogress').empty();
            $('#statslist').empty();
            $('#stable-scanprogress').append('<p>'+'Scan not found'+'</p>');
        }
        else {
            /*Stats updates*/
            $('#statslist-report-count').text(scanreturn['num_reports']);
            $('#statslist-exec-time').text(scanreturn['average_duration']+ ' seconds');
            $('#statslist').show();
            /* Info update*/
            $('#last-exec-scanprogress').text(scanreturn['last_executed']);
            /*Status updates*/
            $('#active-scanprogress').text(scanreturn['active']);
            $('#status-scanprogress').text(scanreturn['scan_status']);
            if (scanreturn['active'] == 'OFF'){
                $('#next-exec-scanprogress').hide();
                $('#scanprogress').hide();
            }
            else{
                $('#next-val-scanprogress').text(scanreturn['next_at']);
                $('#next-exec-scanprogress').show();
                
                if (scanreturn['scan_status'] == "RUNNING"){
                    $('#task-name-scanprogress').text(scanreturn['namet']);
                    $('#task-status-scanprogress').text(scanreturn['status']);
                    $('#task-progress-scanprogress').css('width', scanreturn['progress'] + '%').text(scanreturn['progress'] + '%');
                    $('#scanprogress').show();
                }
                else {
                    $('#scanprogress').hide();
                }
            }
        }
        setTimeout('updateMsg()', 3000);
    });
}
function scansTotals() {
    var url = $("#info-tab-pane").attr("report-url");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          // Update the stats in the scan list view
          $('#scansCreatedTotal').text(data.data.scans_created_total + ' scans CREATED');
          $('#scansActiveTotal').text(data.data.scans_active_total + ' scans ACTIVE');
          $('#scansRunningTotal').text(data.data.scans_running_total + ' scans RUNNING');
        }
      });
}
function scansTableRefresh() {
    // Get the current value of the "active" parameter
    console.log("scansTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimple5").attr("report-url");
    // 
    var table = $('#datatablesSimple5').DataTable( {
        ajax: url,
        columns: [
            { data: 'Flast_executed', title: 'Last Execution at' },
            { data: 'Fnext_execution_at', title: 'Next Execution at' },
            { data: 'scanName', title: 'Name', 
                render: function(data, type, row, meta) {
                    return '<a href=' + '/scans/' + row.id + '>'+row.scanName+'</a>';
                }
            },
            { data: 'Fstatus', title: 'Current Status' },
            { data: 'Factive', title: 'Active' },
            {
              data: 'Fresourcegroup',
              title: 'Group',
              render: function(data, type, row, meta) {
                return '<a href=' + '/groups/' + row.resourcegroup_id + '>'+row.Fresourcegroup+'</a>';
              }
            },
        ],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );
    setInterval(function() {
        table.ajax.reload();
    }, 3000);
}
var handle = null;
function updateChartData() {
    // Make the AJAX request to get the updated data
    var url = $("#scanchart").attr("ajax-target");    
    $.ajax({
      url: url,
      success: function(data) {
        // Update the chart with the new data
        handle.data.labels = data.data.labels;
        handle.data.datasets[0].data = data.data.datasets[0].data;
        handle.update();
      }
    });
  }

function createChart() {
    var url = $("#scanchart").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {

            var ctx = document.getElementById('my-chart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Scans Created', 'Scans Active', 'Scans Running'],
                    datasets: [{
                        label: 'Scans',
                        data: data,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                            'rgba(255, 206, 86, 0.2)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',

                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    }
                }
            });
            
        }
    });
}

function createScanChart() {
    var url = $("#scanchart").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            var ctx = document.getElementById('my-chart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'pie',
                data: data.data,
                options: data.options,
            });
            handle = chart;
        }
    });
    setInterval(updateChartData(), 10000);
}


$(document).ready(function(){
    createScanChart();
    scansTableRefresh();
    scansTotals();
    setInterval(scansTotals, 7000);

    $.ajaxSetup({ cache:false });
    updateMsg();

});