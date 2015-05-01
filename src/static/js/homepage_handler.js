/**
 * Created by rodriga on 3/20/2015.
 */
$(function () {

    $('#nav_list').on('click', 'li', function() {
    $('.nav_list li.active').removeClass('active');
    $(this).addClass('active');
});
    $("#home_nav").click();


    var body = $("html:not(:animated) ,body:not(:animated)"),
        contHello = $('.container__section_welcome'),
        contOne = $(".container__section__one"),

        butWelcome = $('.container__section__welcome .container__button'),
        butOne = $(".container__section__one .container__button"),



        //Parameters
        fullHeight = $(window).height(),
        scrollTop = $(window).scrollTop();




    butWelcome.on('click', function () {
        body.animate({
            scrollTop: fullHeight
        }, {
            queue: false,
            duration: 1000
        });

    });

    butOne.on('click', function () {
        body.animate({
            scrollTop: fullHeight * 2
        }, {
            queue: false,
            duration: 500
        });

    });



 $(this).keydown(function (e) {
        if (e.keyCode == '13') {
            $("#keywordsubmitbtn").submit();
        }
    });

    $("#manualUploadBtn").click(function () {
        if ($('#text').val() == "") {
            alert('The textbox cannot be left blank, enter some text and try again.');
            return false;
        }

    });
});








