function updateMsg() {
    console.log('Requesting scan JSON');
    var urlis = $("#scanprogress").attr("data-ajax-target");
    var spinner = $("#scanprogress").attr("altstuff");
    $.getJSON(urlis, function(scanreturn){
        console.log('JSON', scanreturn);

        /*Status updates*/
        /*if no scan is found by the ajax call*/
        if (scanreturn['scan'] == 0){
            $('#stable-scanprogress').empty();
            $('#scanprogress').empty();
            $('#statslist').empty();
            $('#stable-scanprogress').append('<p>'+'Scan not found'+'</p>');
        }
        else {
            /*Stats updates*/
            $('#statslist-report-count').text(scanreturn['num_reports']);
            $('#statslist-exec-time').text(scanreturn['average_duration']+ ' seconds');
            $('#statslist').show();
            /* Info update*/
            $('#last-exec-scanprogress').text(scanreturn['last_executed']);
            /*Status updates*/
            $('#active-scanprogress').text(scanreturn['active']);
            $('#status-scanprogress').text(scanreturn['scan_status']);
            if (scanreturn['active'] == 'OFF'){
                $('#toggle-button').prop('disabled', false);
                $('#next-exec-scanprogress').hide();
                $('#scanprogress').hide();
            }
            else{

                
                if (scanreturn['scan_status'] == "RUNNING"){
                    $('#toggle-button').prop('disabled', true);
                    $('#task-name-scanprogress').text(scanreturn['namet']);
                    $('#task-status-scanprogress').text(scanreturn['status']);
                    $('#task-progress-scanprogress').css('width', scanreturn['progress'] + '%').text(scanreturn['progress'] + '%');
                    $('#scanprogress').show();
                    $('#next-exec-scanprogress').hide();
                }
                else {
                    $('#toggle-button').prop('disabled', false);
                    $('#scanprogress').hide();
                    $('#next-val-scanprogress').text(scanreturn['next_at']);
                    $('#next-exec-scanprogress').show();
                }
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
          $("#toggle-button").removeClass("btn-success");
          $("#toggle-button").addClass("btn-danger");
          $("#toggle-button").text("TURN OFF");
          $("#active").val("1");
        } else {
          $("#toggle-button").removeClass("btn-danger");
          $("#toggle-button").addClass("btn-success");
          $("#toggle-button").text("TURN ON");
          $("#active").val("0");
        }
      }
    });
  }

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




$(document).ready(function(){
    $('#scanprogress').hide();
    $('#statslist').hide();
    $("#toggle-button").click(function(e){
        e.preventDefault();
        toggleActive();
    });
    reportsTableRefresh();
    
    $.ajaxSetup({ cache:false });
    updateMsg();

});