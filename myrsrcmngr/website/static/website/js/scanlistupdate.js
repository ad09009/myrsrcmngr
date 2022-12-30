
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
    }, 40000);
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
    setInterval(updateChartData(), 20000);
}


$(document).ready(function(){
    createScanChart();
    scansTableRefresh();
    scansTotals();
    setInterval(scansTotals, 20000);

    $.ajaxSetup({ cache:false });

});