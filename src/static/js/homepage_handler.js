/**
 * Created by rodriga on 3/20/2015.
 */
$(function () {

    /*
     Setting up the navigation list so that it sets the correct item as "active" when clicked.
     */
    $('#nav_list').on('click', 'li', function () {
        $('.nav_list li.active').removeClass('active');
        $(this).addClass('active');
    });
    /*
     Set the Home navigation item as "active" since we are on the homepage.
     */
    $("#home_nav").click();


    /*
     This is the code for the "parallax" like scrolling on homepage that allows the user to transition to the lower portion of the page by clicking the down arrow on the page.
     */
    var body = $("html:not(:animated) ,body:not(:animated)"),

        butWelcome = $('.container__section__welcome .container__button'),

    //Parameters
        fullHeight = $(window).height();

    butWelcome.on('click', function () {
        body.animate({
            scrollTop: fullHeight
        }, {
            queue: false,
            duration: 1000
        });

    });

    /*
     This enables for users to use the "enter" key to submit on ID and keyword searches
     */
    $(this).keydown(function (e) {
        if (e.keyCode == '13') {
            $("#keywordsubmitbtn").submit();
        }
    });

    /*
     Error handling to catch a user trying to submit an empty text box on manual upload.
     */
    $("#manualUploadBtn").click(function () {
        if ($('#text').val() == "") {
            alert('The textbox cannot be left blank, enter some text and try again.');
            return false;
        }

    });
});








