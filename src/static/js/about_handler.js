/**
 * Created by rodriga on 5/2/2015.
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
     Set the About navigation item as "active".
     */
    $("#about_nav").click();
});