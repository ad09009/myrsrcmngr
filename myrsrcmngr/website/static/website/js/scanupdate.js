function updateMsg() {
    console.log('Requesting scan JSON');
    var urlis = $("#scanprogress").attr("data-ajax-target");
    var spinner = $("#scanprogress").attr("altstuff");
    $.getJSON(urlis, function(scanreturn){
        console.log('JSON', scanreturn);
        $('#scanprogress').empty();

        if (scanreturn['scan'] == 0){
            /*$('#scanprogress').append('<img src='+spinner+' alt="Loading..."/>');*/
            $('#scanprogress').append('<p>'+'Scan not found'+'</p>');
        }
        else {
            if (scanreturn['active'] == 'Off'){
                $('#scanprogress').append('<p>'+'Scan is: '+' OFF'+'</p>');
            }
            else{
                $('#scanprogress').append('<p>'+'Scan is: '+' ON'+'</p>');
                if (scanreturn['status'] != 2){
                    $('#scanprogress').append('<p>'+'Scan is: '+'DONE'+'</p>');
                    $('#scanprogress').append('<p> Next scan: '+scanreturn['next_at']+'</p><br>');
                }

                
                    $('#scanprogress').append('<p> Task status: '+scanreturn['status']+'</p>');
                    $('#scanprogress').append('<p> Task name: '+scanreturn['name']+'</p>');
                    $('#scanprogress').append('<p> Task etc: '+scanreturn['etc']+'</p>');
                    $('#scanprogress').append('<p> Task progress: '+scanreturn['progress']+'% </p>');
                

            }
        }
        setTimeout('updateMsg()', 3000);
    });
}

$(document).ready(function(){
    $.ajaxSetup({ cache:false });
    updateMsg();
});