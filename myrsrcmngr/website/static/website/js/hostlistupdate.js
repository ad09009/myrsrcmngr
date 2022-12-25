
  function hostsTableRefresh() {
    // Get the current value of the "active" parameter
    console.log("hostsTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimpleGrHo").attr("report-url");
    // 
    var table = $('#datatablesSimpleGrHo').DataTable( {
        ajax: url,
        columns: [
            {
                data: 'main_address',
                title: 'Main Address',
                render: function(data, type, row, meta) {
                return '<a href=' + '/hosts/' + row.id + '>' + row.main_address + '</a>';
                }
            },
            { data: 'hostnames', title: 'Hostnames' },
            { data: 'status', title: 'Status' },
            { data: 'mac', title: 'MAC Address' },
            { data: 'os_fingerprint', title: 'OS Fingerprint' },
            { data: 'num_of_services', title: 'Number of Services' },
            {
                data: 'rgroupid',
                title: 'Group',
                render: function(data, type, row, meta) {
                return '<a href=' + '/groups/' + row.rgroupid + '>' + row.rgroupname + '</a>';
                }
            },
        ],
        pageLength: 10,
        order: [[2, 'desc']],
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );
    setInterval(function() {
        table.ajax.reload();
    }, 10000);
}

  function hostsTotals() {
    var url = $("#host-info-tab-pane").attr("report-url");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          // Update the stats in the scan list view
          $('#hostsCreatedTotal').text(data.data.total_hosts + ' hosts TOTAL');
          $('#hostsUpTotal').text(data.data.total_hosts_up + ' hosts UP');
          $('#hostsDownTotal').text(data.data.total_hosts_down + ' hosts DOWN');
        }
      });
}

var handle = null;
function updateChartData() {
    // Make the AJAX request to get the updated data
    var url = $("#hostchartWrapper").attr("ajax-target");    
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

function createHostChart() {
    var url = $("#hostchartWrapper").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {

            var ctx = document.getElementById('hostChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'bar',
                data: data.data,
                options: data.options,
            });
            handle = chart;
            
        }
        
    });
    setInterval(updateChartData(), 10000);
}


$(document).ready(function(){
    createHostChart();
    hostsTotals();
    setInterval(hostsTotals(), 7000);
    hostsTableRefresh();

});