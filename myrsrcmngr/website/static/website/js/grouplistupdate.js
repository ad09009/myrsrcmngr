
function groupsTotals() {
    var url = $("#group-info-tab-pane").attr("report-url");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
          // Update the stats in the scan list view
          $('#scansCreatedTotal').text(data.data.groups_created_total + ' groups CREATED');
          $('#scansActiveTotal').text(data.data.groups_scans_total + ' scans TOTAL');
          $('#scansRunningTotal').text(data.data.groups_hosts_total + ' hosts TOTAL');
        }
      });
}
function groupsTableRefresh() {
    // Get the current value of the "active" parameter
    console.log("groupsTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimple6").attr("report-url");
    // 
    var table = $('#datatablesSimple6').DataTable( {
        ajax: url,
        columns: [
            { data: 'Fadd_date', title: 'Creation Date' },
            { data: 'Fupdated_at', title: 'Modification Date' },
            { data: 'username', title: 'Created by', 
                render: function(data, type, row, meta) {
                    return '<a href=' + '/profile/' + row.Fuser + '>'+row.username+'</a>';
                }
            },
            { data: 'subnet', title: 'Subnet' },
            { data: 'name', title: 'Name', 
                render: function(data, type, row, meta) {
                    return '<a href=' + '/groups/' + row.id + '>'+row.name+'</a>';
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
function updateGrChartData() {
    // Make the AJAX request to get the updated data
    var url = $("#groupChartWrapper").attr("ajax-target");    
    var chart = $('#groupChart').get(0).getContext('2d').chart;
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

function createGroupChart() {
    var url = $("#groupChartWrapper").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            var ctx = document.getElementById('groupChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'pie',
                data: data.data,
                options: data.options,
            });
            handle = chart;
        }
    });
    setInterval(updateGrChartData(), 20000);
}

$(document).ready(function(){
    createGroupChart();
    groupsTableRefresh();
    groupsTotals();
    setInterval(groupsTotals(), 21000);

    $.ajaxSetup({ cache:false });

});