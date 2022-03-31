$(document).ready(function () {

    $('.btn-banner').click(function () {
        if ($(".btn-banner").text() == "Вход") {
            $(".btn-banner").text("Назад");
        } else {
            $(".btn-banner").text("Вход");
        }
        $('.hidden-login-form, .banner-welcome').toggle("slow");
    });

    $(".flex-slide").each(function () {
        $(this).hover(function () {
            $(this).find('.flex-title').css({
                transform: 'rotate(0deg)',
                top: '10%'
            });
            $(this).find('.flex-about').css({
                opacity: '1'
            });
        }, function () {
            $(this).find('.flex-title').css({
                transform: 'rotate(90deg)',
                top: '15%'
            });
            $(this).find('.flex-about').css({
                opacity: '0'
            });
        })
    });

    $("#subject option:first").attr("disabled", "disabled");


    if ($('.login-errors').val() == 1) {
        jQuery(function () {
            jQuery('#banner_btn').click();
        });
    }


});

