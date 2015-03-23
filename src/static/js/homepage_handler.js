/**
 * Created by rodriga on 3/20/2015.
 */
$(function () {

   $("#manualUploadBtn").click(function () {
       if ($('#text').val() == "") {
           alert('The textbox cannot be left blank, enter some text and try again.');
           return false;
       }



   });
});



