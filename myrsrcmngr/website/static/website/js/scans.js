//write a javascript function that will be called when the a tag with id "active" is clicked.
//When called this function will send a post request to the server with the scan id and the status of the scan, to change the active flag to either on or off depending on the status of the scan.
//The function will also change the color of the a tag to green if the scan is active and red if the scan is inactive.
//The function will also change the text of the a tag to "Active" if the scan is active and "Inactive" if the scan is inactive.

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