
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

function createItem(change, i) {
    var option = "";
    var active = "";
    if (i === 0) {
        active = "active";
    }
    if (change.attribute === "state") {
        option = itemTemplate(1, "New Open Port", active, change.main_address, change.host_id, change.group_name, change.group_id, change.new_value, change.report_date, change.report_id);
    }
    else if (change.attribute === "os_fingerprint") {
        option = itemTemplate(1, "OS Fingerprint Altered", active, change.main_address, change.host_id, change.group_name, change.group_id, change.new_value, change.report_date, change.report_id);
    }
    else if (change.attribute === "status") {
        option = itemTemplate(1, "Host State Changed", active, change.main_address, change.host_id, change.group_name, change.group_id, change.new_value, change.report_date, change.report_id);
    }
    else {
        option = itemTemplate(1, "Change", active, change.main_address, change.host_id, change.group_name, change.group_id, change.new_value, change.report_date, change.report_id);
    }
    console.log(change);
    return option;

  }

function itemTemplate(type, title, active, host, host_id, group, group_id, value, report_date, report_id){
    if (type === 1){
        var emptyitem = `<div class="carousel-item ${active}">
        <div class="card-body mx-auto text-center">
        <h5 class="card-title text-center">${title}</h5>
        <div class="row">
            <div class="col-6">Host: </div>
            <div class="col-6 text-right"><a href="/hosts/${host_id}">${host}</a></div>
        </div> 
        <div class="row">
            <div class="col-6">Group: </div>
            <div class="col-6 text-right"><a href="/hosts/${group_id}">${group}</a></div>
        </div> 
        <div class="row">
            <div class="col-6">Change: </div>
            <div class="col-6 text-right">${value}</div>
        </div> 
        <div class="row">
            <div class="col-6">Report: </div>
            <div class="col-6 text-right"><a href="/hosts/${report_id}">${report_date}</a></div>
        </div> 
        </div>
        </div>` ;
    }
    else {
        var emptyitem = `<div class="carousel-item active">
        <div class="card-body mx-auto text-center">
    <h5 class="card-title text-center">No New Changes</h5>
    <div class="row">
        <div class="col-6">Host: </div>
        <div class="col-6 text-right">-</div>
    </div> 
    <div class="row">
        <div class="col-6">Group: </div>
        <div class="col-6 text-right">-</div>
    </div> 
    <div class="row">
        <div class="col-6">Change: </div>
        <div class="col-6 text-right">-</div>
    </div> 
    <div class="row">
        <div class="col-6">Report: </div>
        <div class="col-6 text-right">-</div>
    </div> 
    </div>
    </div>`;
    }
    return emptyitem;
}

function updateChangesCarousel(data) {
    var totals = data.total;
    var data = data.changes;
    if (data.length > 0) {
        $('#dashboardDismiss').prop('disabled', false);
        $("#active").val("0");
        // clear the carousel
        $('#innerC').empty();
        console.log("data length > 0", data.length);
        $('#allChanges').text('View All '+ totals +' Changes');
        $('#allChanges').removeClass('disabled');
        $('#allChanges').prop('href', '/changes/');
        for (let i = 0; i < data.length; i++) {
            let change = data[i];
            let newItem = createItem(change, i);
            // create a new carousel item for this change
            $('#innerC').append(newItem);
        }
        $('#changes-carousel').carousel('refresh');
    }
    else{
        $('#dashboardDismiss').prop('disabled', true);
        $('#allChanges').addClass('disabled');
        $('#allChanges').prop('href', '#');
    }
  }


function getChanges() {
    var url = $("#dashboardChanges").attr("data-ajax-target");

    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            updateChangesCarousel(data.data);
        }
    });
}


function dismissChanges() {
    console.log("dismissChanges");
    var currentValue = $("#active").val();
    const csrftoken = getCookie('csrftoken');
    // Flip the value of the "active" parameter
    var newValue = (currentValue === "0") ? "1" : "0";
    var url = $("#dashboardDismiss").attr("scan-ajax-target");
    // Use AJAX to send a POST request to update the value of the "active" parameter
    if (currentValue === "0") {
        $.ajax({
            type: "POST",
            url: url,
            data: {},
            headers: {
              "X-CSRFToken": csrftoken
              },
            success: function(response) {
              // update the carousel to show "No new changes"
              $('#innerC').empty();
              $('#allChanges').text('View All 0 Changes');
              $('#allChanges').addClass('disabled');
              $('#allChanges').prop('href', '#');
              $('#innerC').append(itemTemplate(0));
                $('#changes-carousel').carousel('refresh');
              $("#active").val("1");
              $('#dashboardDismiss').prop('disabled', true);
            },
            error: function(xhr, status, error) {
              // code to execute on error
              console.error('Error dismissing changes: ' + error);
              }
          });
    }
    else{
        console.log("dismissChanges: no changes to dismiss");
    }
    
}

function viewChanges() {
   
    console.log("viewChanges");
    $('#viewChangesContainer').hide();
    $('#changes-carousel').carousel('show');
    
}
var handle = null;
function updateChartData() {
    // Make the AJAX request to get the updated data
    var url = $("#dashchartWrapper").attr("ajax-target");    
    $.ajax({
      url: url,
      success: function(data) {
        // Update the chart with the new data
        handle.data.labels = data.data.labels;
        handle.data.datasets[0].data = data.data.datasets[0].data;
        handle.update();
      }
    });
  }

function createDashboardChart() {
    var url = $("#dashchartWrapper").attr("ajax-target");
    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(data) {

            var ctx = document.getElementById('dashboardChart').getContext('2d');
            var chart = new Chart(ctx, {
                type: 'bar',
                data: data.data,
                options: data.options,
            });
            handle = chart;
            
        }
        
    });
    setInterval(updateChartData(), 20000);
}

function scansDashboardRefresh() {
    // Get the current value of the "active" parameter
    console.log("scansTableRefresh");
    // Get the URL of the page to request the table data from
    var url = $("#datatablesSimpleDashScans").attr("report-url");
    // 
    var table = $('#datatablesSimpleDashScans').DataTable( {
        ajax: url,
        columns: [
            { data: 'scanName', title: 'Name', 
                render: function(data, type, row, meta) {
                    return '<a href=' + '/scans/' + row.id + '>'+row.scanName+'</a>';
                }
            },
            {
              data: 'Fresourcegroup',
              title: 'Group',
              render: function(data, type, row, meta) {
                return '<a href=' + '/groups/' + row.resourcegroup_id + '>'+row.Fresourcegroup+'</a>';
              }
            },
            { data: 'Fstatus', title: 'Status' },
        ],
        order: [[2, 'desc']],
        searching: false,
        lengthChange: false,
        paging: false,
        info: false,
    } );
    setInterval(function() {
        table.ajax.reload();
    }, 100000);
}

$(document).ready(function(){
    scansDashboardRefresh();
    
    
    createDashboardChart();
    $('#changes-carousel').carousel();
    $("#dashboardDismiss").click(function(e){
        e.preventDefault();
        dismissChanges();
    });
    getChanges();
    setInterval(getChanges, 10000);
});