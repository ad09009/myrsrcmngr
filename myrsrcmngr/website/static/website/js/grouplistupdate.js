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
    }, 3000);
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
    setInterval(updateGrChartData(), 10000);
}

$(document).ready(function(){
    createGroupChart();
    groupsTableRefresh();
    groupsTotals();
    setInterval(groupsTotals(), 7000);

    $.ajaxSetup({ cache:false });
    updateMsg();

});