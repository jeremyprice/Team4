/**
 * Created by rodriga on 1/12/2015.
 */
$(function () {
    $('#submit').click(function () {

        var form_data = new FormData($('#uploadform')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json'
        }).done(function (data) {
            $('#hashtags').text(data['hashtags']);
            $('#original_text').text(data['text']);
            $('#abstract_id').text(data['abstract_id']);

        }).fail(function (data) {
            alert('error!');
        });


    });

});


