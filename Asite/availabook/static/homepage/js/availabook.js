$(document).ready(function() {
    console.log("ready!");

    $("#like_btn").on("click", function() {
        console.log("Like!");

        $.ajax({
            url : "/availabook/get_fave/",
            type : "POST",
            data : {
                fave : $("#like_btn").val()
            },

            success : function(msg) {
                console.log(msg);
                //$("body").html(msg);
                if (msg != {}) {
                    console.log(msg.EId);
                    console.log(msg.fave_num);
                    document.getElementById(msg.EId).innerHTML=msg.fave_num + "-likes";
                    console.log("Like success!");
                    //window.location.reload();
                } else {
                    alert("Please log in first!");
                }
            },

            error : function(xhr,errmsg,err) {
                console.log("Like " + errmsg);
            }
        });
    });

    $("#home_logout_btn").on("click", function() {
        console.log("logout!");
        $.ajax({
            url : "/availabook/logout/",
            type : "GET",

            success : function(msg) {
                //$("body").html(msg);
                console.log("logout success!");
                window.location.reload();
            },

            error : function(xhr,errmsg,err) {
                console.log("logout " + errmsg);
            }
        })
    })

        $("#home_profile_btn").on("click", function() {
        console.log("profile!");
        $.ajax({
            url : "/availabook/profile/",
            type : "GET",

            success : function(msg) {
                //$("body").html(msg);
                console.log("profile success!");
                window.location.reload();
            },

            error : function(xhr,errmsg,err) {
                console.log("profile " + errmsg);
            }
        })
    });

    $("#login_btn").on("click", function(event) {
        event.preventDefault();
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
                // remove the value from the input
                $("#login_id").val("");
                $("#login_psw").val("");
                //$("body").html(msg);
                console.log(msg)
                console.log("login success!"); // another sanity check
                window.location.reload();
                window.location.href = "/availabook/home";
            },

            // handle a non-successful response
            error : function(xhr,errmsg,err) {
                console.log("login" + errmsg);
            // console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    });

    $("#signup_btn").on("click", function(event) {
        event.preventDefault();
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
                $("#signup_email").val("");
                $("#signup_psw").val("");
                $("#signup_psw_a").val("");
                $("#signup_fn").val("");
                $("#signup_ln").val("");
                $("#signup_age").val("");
                $("#signup_city").val("");
                $("#signup_zipcode").val("");
                //$("body").html(msg);
                console.log("signup success!");
                window.location.reload();
                window.location.href = "/availabook/home";
            },

            error : function(xhr,errmsg,err) {
                console.log("signup" + errmsg);
            }
        });
    });

    $("#post_btn").on("click", function() {
        console.log("Post!");
        $.ajax({
            url : "/availabook/post_event/",
            type : "POST",
            data : {
                post_content : $("#post_content").val(),
                dateandtime: $("#dateandtime").val()
            },

            success : function(msg) {
                //$("body").html(msg);
                $("#post_content").val("");
                $("#dateandtime").val("");
                console.log("Put success!");
                window.location.reload();
            },

            error : function(xhr,errmsg,err) {
                console.log("logout" + errmsg);
            }
        })
    });

    $("#like_btn").mouseup(function(){
        $(this).blur();
    });

    $("#outer_post_btn").mouseup(function(){
        $(this).blur();
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

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

$(function () {
  $('[data-toggle="popover"]').popover()
})
