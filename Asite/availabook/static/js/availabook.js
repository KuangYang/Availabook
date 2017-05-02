$(document).ready(function() {
    console.log("ready!");

    // Get the modal and when the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        var modals = document.getElementsByClassName('modal');
        for (var i = 0; i <  modals.length; i++) {
            if (event.target == modals[i]) {
            modals[i].style.display = "none";
            }
        }
    };
});


function login(formData) {
    id = formData['id']
    psw = formData['psw']
    cleanData = {};
    cleanData['info'] = {
        'id':       id,
        'password': psw]
    }
    console.log(id);
    
    $.ajax({
        type: "POST",
        url: 'https://127.0.0.1/availabook/login',
        crossDomain: true,
        contentType: 'application/json',
        data: JSON.stringify(cleanData),
        dataType: 'json',
        success: function(service_data){
           if (service_data['status']=='success'){
               accountDisplayHandler.logIn(formData.email);
               $('#loginModal').modal('hide')
               //set jwt_token
               setCookie("jwt_token", service_data['jwt']);
           }
           else{
               alert("Invalid email or password.");
               accountDisplayHandler.logOut();
           }
        },
        error: function (e) {
           alert("error");
           accountDisplayHandler.logOut();
        }
    });
}
