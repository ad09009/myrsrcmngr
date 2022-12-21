window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki
    $('#datatablesSimple').DataTable( {
        paging: true,
        order: [[1, 'asc']],
        } );
    $('#datatablesSimple2').DataTable( {
        "ajax": "/scans/json/",
        "columns": [
            {"scans":"last_executed"},
            {"scans":"next_execution_at"},
            {"scans":"scanName"},
            {"scans":"status"},
            {"scans":"active"},
            {"scans":"resourcegroup"}
        ],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
        } );
});
