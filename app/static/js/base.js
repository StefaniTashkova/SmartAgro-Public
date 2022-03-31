$(document).ready(function () {
    $("#navbar-top").addClass("normal");
    $(".section").mouseenter(function () {
        var id = $(this).attr('id');
        $('a').removeClass('active');
        $("[href=#" + id + "]").addClass('active');
    });


    $('#login_link').click(function () {
        jQuery(function () {
            jQuery('#banner_btn').click();
        });
    });

    $(window).on("scroll", function () {
        if
        ($(window).scrollTop() > 86) {
            $("#navbar-top").removeClass("normal");
            $("#navbar-top").addClass("shrink");
        } else {
            $("#navbar-top").removeClass("shrink");
            $("#navbar-top").addClass("normal");
        }
        if ($(this).scrollTop() >= $('#about').position().top - 250) {
            $('aside.left-content').slideDown(1000);
           $('aside.right-content').slideDown(1000);
       } else {
           $('aside.left-content').slideUp(20);
           $('aside.right-content').slideUp(20);
       }
    });

});

