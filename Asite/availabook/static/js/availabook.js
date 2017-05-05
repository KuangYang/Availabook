$(document).ready(function() {
    console.log("ready!");

    $("#home_logout_btn").on("click", function() {
        console.log("logout!");
        $.ajax({
            url : "/availabook/logout/",
            type : "GET",

            success : function(msg) {
                $("body").html(msg);
                console.log("logout success!");
            },

            error : function(xhr,errmsg,err) {
                console.log("logout" + errmsg);
            }
        })
    })

    $("#login_btn").on("click", function() {
        console.log("login!");

        $.ajax({
            /* Use absolute url */
            url : "/availabook/login/", // the endpoint
            type : "POST", // http method
            data : {
                id : $("#login_id").val(),
                psw: $("#login_psw").val()
            }, // data sent with the post request

        // handle a successful response
            success : function(msg) {
                $("body").html(msg);
                console.log(msg)
                $("#login_id").val("");
                $("#login_psw").val("");// remove the value from the input
                console.log("login success!"); // another sanity check
            },

        // handle a non-successful response
            error : function(xhr,errmsg,err) {
                console.log("login" + errmsg);
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    });

    $("#signup_btn").on("click", function() {
        console.log("signup!");

        $.ajax({
            url : "/availabook/signup/",
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

            success : function(msg) {
                $("body").html(msg);
                console.log("signup success!");
            },

            error : function(xhr,errmsg,err) {
                console.log("signup" + errmsg);
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
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrftoken = getCookie('csrftoken');

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
