$(document).ready(function() {
    console.log("ready!");

    $("#signup_btn").on("click", function() {
        console.log("signup!");

        $.ajax({
            url : "signup/",
            type : "POST",
            data : {
                email : $("#signup_email").val(),
                psw : $("#signup_psw").val(),
                psw_a : $("#signup_psw_a").val(),
                fn : $("#signup_fn").val(),
                ln : $("#signup_ln").val(),
                age : $("#signup_age").val(),
                city : $("#signup_city").val(),
                zipcode : $("#signup_zipcode").val()
            },

            success : function(json) {
                console.log("success");
            },

            error : function(xhr,errmsg,err) {
                console.log(errmsg);
            }
        });

        var home_login_btn = document.getElementById("home_login_btn");
        home_login_btn.style.display = "none";
        var home_signup_btn = document.getElementById("home_signup_btn");
        home_signup_btn.style.display = "none";
    });

    $("#login_btn").on("click", function() {
        console.log("login!");

        $.ajax({
            url : "login/", // the endpoint
            type : "POST", // http method
            data : {
                id : $("#login_id").val(),
                psw: $("#login_psw").val()
            }, // data sent with the post request

        // handle a successful response
            success : function(json) {
                $("#login_id").val("");
                $("#login_psw").val("");// remove the value from the input
                console.log("success"); // another sanity check

                var home_login_btn = document.getElementById("home_login_btn");
                home_login_btn.style.display = "none";
                var home_signup_btn = document.getElementById("home_signup_btn");
                home_signup_btn.style.display = "none";
                document.getElementById("login").style.display='block';
            },

        // handle a non-successful response
            error : function(xhr,errmsg,err) {
                console.log(errmsg);
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    });

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

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function login(formData) {
    id = formData['id']
    psw = formData['psw']
    cleanData = {};
    cleanData['info'] = {
        'id':       id,
        'password': psw,
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
