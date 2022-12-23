$('#datatablesSimpleGrHo').DataTable( {
    paging: true,
    order: [[1, 'asc']],
    } );

$('#datatablesSimpleGrSc').DataTable( {
    paging: true,
    order: [[1, 'asc']],
    } );

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
    groupTotals();
    setInterval(groupTotals, 7000);
    // Simple-DataTables
    //
});