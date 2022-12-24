

function HostsTables() {

    var table = $('#datatablesSimpleHoSe').DataTable( {
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );

    var table = $('#datatablesSimpleHoCh').DataTable( {
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );
}

$(document).ready(function(){
    $('#datatablesSimpleHoSe').DataTable( {
        order: [[1, 'desc']],
        pageLength: 10,
        lenghtChange: true,
        autoWidth: false,
        searching: true,
        bInfo: true,
        bSort: true,
        paging: true
    } );

    $('#datatablesSimpleHoCh').DataTable( {
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