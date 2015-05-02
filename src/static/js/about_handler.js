/**
 * Created by rodriga on 5/2/2015.
 */
$(function () {

    $('#nav_list').on('click', 'li', function () {
        $('.nav_list li.active').removeClass('active');
        $(this).addClass('active');
    });
    $("#about_nav").click();
});