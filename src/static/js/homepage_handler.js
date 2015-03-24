/**
 * Created by rodriga on 3/20/2015.
 */
$(function () {


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



