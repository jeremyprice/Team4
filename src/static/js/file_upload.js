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

            $('#abstract_id').text(data['abstract_id']);




            for( var i=0; i < data['tokenized_text'].length; i++){
               testWord(data['tokenized_text'][i], data['highlighted_text'])
            }


        }).fail(function (data) {
            alert('error!');
        });


    });

});

function testWord(word, highlightedWords) {
    for (var i = 0; i < highlightedWords.length; i++) {
        if (word == highlightedWords[i]) {
            var newSpan = null;
            newSpan = document.createElement('span');
            newSpan.setAttribute('class', 'testSpan');
            $('#original_text').append(newSpan);
            $(newSpan).text(word+" ");
            break;
        }
            var newSpan = null;
            newSpan = document.createElement('span');
            $('#original_text').append(newSpan);
            $(newSpan).text(word+" ");
            break;
    }
}


