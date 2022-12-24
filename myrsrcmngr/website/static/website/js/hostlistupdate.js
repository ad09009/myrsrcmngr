
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
          $('#hostsCreatedTotal').text(data.totals.total_hosts + ' hosts TOTAL');
          $('#hostsUpTotal').text(data.totals.total_hosts_up + ' hosts UP');
          $('#hostsDownTotal').text(data.totals.total_hosts_down + ' hosts DOWN');
        }
      });
}


$(document).ready(function(){
    hostsTotals();
    setInterval(hostsTotals(), 7000);
    hostsTableRefresh();

});