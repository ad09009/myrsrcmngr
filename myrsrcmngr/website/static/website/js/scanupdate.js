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
                $('#scanprogress').append('<p class="card-text">'+'Scan is: '+' ON'+'</p>');
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
function toggleActive3() {
    var url = $("#activebutton").attr("scan-ajax-target");
    var id = $("#activebutton").attr("scan-id");
    $("#activebutton").click(function(e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: url,
            data: { 
                active: $(this).val(),
                id: id 
            },
            success: function(result) {
                if (!result){
                    $("#activebutton").css("background-color", "green");
                    $("#activebutton").text("Active");
                    $("#activebutton").val(1);
                }else{
                    $("#activebutton").css("background-color", "red");
                    $("#activebutton").text("Inactive");
                    $("#activebutton").val(0);
                }
                alert('ok');
                console.log(result);
            },
            error: function(result) {
                alert('error');
                console.log(result);
            }
        });
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function toggleActive() {
    // Get the current value of the "active" parameter
    console.log("toggleActive");
    var currentValue = $("#active").val();
    const csrftoken = getCookie('csrftoken');
    // Flip the value of the "active" parameter
    var newValue = (currentValue === "0") ? "1" : "0";
    var url = $("#toggle-button").attr("scan-ajax-target");
    console.log(url);
    // Use AJAX to send a POST request to update the value of the "active" parameter
    $.ajax({
      type: "POST",
      url: url,
      data: { active: newValue },
      headers: {
        "X-CSRFToken": csrftoken
        },
      success: function(response) {
        // Update the color and text of the button to reflect the new value of the "active" parameter
        if (newValue === "1") {
          $("#toggle-button").css("background-color", "green");
          $("#toggle-button").text("On");
          $("#active").val("1");
        } else {
          $("#toggle-button").css("background-color", "red");
          $("#toggle-button").text("Off");
          $("#active").val("0");
        }
      }
    });
  }



$(document).ready(function(){
    console.log("ready");
    $("#toggle-button").click(function(e){
        console.log("click");
        e.preventDefault();
        toggleActive();
    });
    console.log("ready2");
    $.ajaxSetup({ cache:false });
    updateMsg();

});