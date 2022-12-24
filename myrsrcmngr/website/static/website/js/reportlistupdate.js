
  function reportsTableRefresh() {
    // Get the current value of the "active" parameter
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
    }, 3000);
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


$(document).ready(function(){
    reportsTotals();
    setInterval(reportsTotals(), 7000);
    reportsTableRefresh();

});