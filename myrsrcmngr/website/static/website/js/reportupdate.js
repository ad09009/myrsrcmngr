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

function toggleStandard() {
    // Get the current value of the "active" parameter
    console.log("toggleStandard");
    var currentValue = $("#standard").val();
    const csrftoken = getCookie('csrftoken');
    // Flip the value of the "active" parameter
    var newValue = (currentValue === "0") ? "1" : "0";
    var url = $("#toggle-standard").attr("scan-ajax-target");
    // Use AJAX to send a POST request to update the value of the "active" parameter
    $.ajax({
      type: "POST",
      url: url,
      data: { standard: newValue },
      headers: {
        "X-CSRFToken": csrftoken
        },
      success: function(response) {
        // Update the color and text of the button to reflect the new value of the "active" parameter
        if (newValue === "1") {
          $("#toggle-standard").removeClass("btn-success");
          $("#toggle-standard").addClass("btn-danger");
          $("#toggle-standard").text("Remove as Standard");
          $("#standard").val("1");
          
          $("#standardCheck").removeClass("fa-times");
          $("#standardCheck").removeClass("text-danger");
          $("#standardCheck").addClass("fa-check");
          $("#standardCheck").addClass("text-success");

        } else {
          $("#toggle-standard").removeClass("btn-danger");
          $("#toggle-standard").addClass("btn-success");
          $("#toggle-standard").text("Set as Standard");
          $("#standard").val("0");

          $("#standardCheck").removeClass("fa-check");
          $("#standardCheck").removeClass("text-success");
          $("#standardCheck").addClass("fa-times");
          $("#standardCheck").addClass("text-danger");
        }
      }
    });
  }

$(document).ready(function(){
    $("#toggle-standard").click(function(e){
        e.preventDefault();
        toggleStandard();
    });

});