function GroupHostsTableRefresh() {
    // Get the current value of the "active" parameter
    console.log("GroupHostsTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimpleGrHo").attr("report-url");
    // 
    var table = $('#datatablesSimpleGrHo').DataTable( {
        ajax: url,
        columns: [
            { data: 'main_address', title: 'Main Address' },
            { data: 'hostnames', title: 'Hostnames' },
            { data: 'status', title: 'Status' },
            { data: 'mac', title: 'MAC Address' },
            { data: 'os_fingerprint', title: 'OS Fingerprint' },
            { data: 'num_of_services', title: 'Number of Services' },
            {
                data: 'id',
                title: 'URL',
                render: function(data, type, row, meta) {
                console.log('datatablesSimpleGrHo')
                return '<a href=' + '/hosts/' + row.id + '>View Host</a>';
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
    }, 10000);
}

function GroupScansTableRefresh() {
    // Get the current value of the "active" parameter
    console.log("GroupScansTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimpleGrSc").attr("report-url");
    // 
    var table2 = $('#datatablesSimpleGrSc').DataTable( {
        ajax: url,
        columns: [
            { data: 'Flast_executed', title: 'Last Execution at' },
            { data: 'Fnext_execution_at', title: 'Next Execution at' },
            {
                data: 'id',
                title: 'Name',
                render: function(data, type, row, meta) {
                console.log('datatablesSimpleGrSc')
                return '<a href=' + '/scans/' + row.id + '>' + row.scanName + '</a>';
                }
            },
            { data: 'Fstatus', title: 'Current Status' },
            { data: 'Factive', title: 'Active' },
            
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
        table2.ajax.reload();
    }, 10000);
}

function groupTotals() {
    var url = $("#groupchanges").attr("data-ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            // Update the status in the group view
            $('#totalscans-groupstatus').text(data.data.scans_count);
            $('#activescans-groupstatus').text(data.data.active_scans_count);
            $('#runningscans-groupstatus').text(data.data.running_scans_count);

            $('#hostsup-groupstatus').text(data.data.hostsup_count);
            $('#hostsdown-groupstatus').text(data.data.hostsdown_count);
            $('#hoststotal-groupstatus').text(data.data.hosts_count);
        }
        });
}
    
$(document).ready(function(){
    GroupHostsTableRefresh();
    GroupScansTableRefresh();
    groupTotals();
    setInterval(groupTotals, 7000);

});