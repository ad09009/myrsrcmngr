
  function reportsTableRefresh() {
    console.log("reportsTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimple4").attr("report-url");
    // 
    var table = $('#datatablesSimple4').DataTable( {
        ajax: url,
        columns: [
            { data: 'fstarted', title: 'Started at' },
            { data: 'fended', title: 'Ended at' },
            { data: 'elapsed', title: 'Duration (in seconds)' },
            { data: 'num_services', title: 'Number of Services' },
            { data: 'hosts_up', title: 'Hosts Up' },
            { data: 'hosts_down', title: 'Hosts Down' },
            { data: 'hosts_total', title: 'Hosts Total' },
            {
              data: 'id',
              title: 'URL',
              render: function(data, type, row, meta) {
                        return row.fstarted === null ? row.summary : '<a href=' + '/reports/' + row.id + '>View Report</a>';
              }
            },
        ],
        order: [[0, 'desc']],
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
    }, 7000);
  }

  function reportsTotals() {
    var url = $("#report-info-tab-pane").attr("report-url");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          // Update the stats in the scan list view
          $('#scansCreatedTotal').text(data.total_reports + ' total reports created');
          $('#scansActiveTotal').text(data.total_success_reports + ' succesfully parsed');
          $('#scansRunningTotal').text(data.total_failed_reports + ' failed');
        }
      });
}

var handle = null;
function updateChartData() {
    // Make the AJAX request to get the updated data
    var url = $("#reportchartWrapper").attr("ajax-target");    
    $.ajax({
      url: url,
      success: function(data) {
        // Update the chart with the new data
        handle.data.labels = data.data.labels;
        for (var i = 0; i < handle.data.datasets.length; i++) {
          handle.data.datasets[i].data = data.data.datasets[i].data;
        }
        handle.update();
      }
    });
  }

function createReportChart() {
    var url = $("#reportchartWrapper").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {

            var ctx = document.getElementById('reportChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'line',
                data: data.data,
                options: data.options,
            });
            handle = chart;
            
        }
        
    });
    setInterval(updateChartData(), 15000);
}


$(document).ready(function(){
    reportsTotals();
    createReportChart();
    setInterval(reportsTotals(), 10000);
    reportsTableRefresh();

});