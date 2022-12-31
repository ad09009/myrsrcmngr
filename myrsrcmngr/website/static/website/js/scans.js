
function changeActive(scan_id, status){
    console.log("Scan id: " + scan_id + " Status: " + status);
    $.ajax({
        url: '/scans/change_active',
        type: 'POST',
        data: {scan_id: scan_id, status: status},
        success: function(data){
            if(data == "on"){
                $("#active").css("background-color", "green");
                $("#active").text("Active");
                $("#active").val("on");
            }else{
                $("#active").css("background-color", "red");
                $("#active").text("Inactive");
                $("#active").val("off");
            }
        }
    });
    console.log("Scan id: " + scan_id + " Status: " + status);
}