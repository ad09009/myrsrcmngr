$(document).ready(function(){
    $('#datatablesSimpleChanges').DataTable( {
        order: [[5, 'desc']],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );
});