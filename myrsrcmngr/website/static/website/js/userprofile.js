$(document).ready(function(){
    $('#datatablesSimpleUserGroups').DataTable( {
        order: [[0, 'desc']],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );
    $('#datatablesSimpleUserScans').DataTable( {
        order: [[0, 'desc']],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );

});