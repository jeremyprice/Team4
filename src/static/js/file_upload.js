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

            for (var i = 0; i < data['tokenized_text'].length; i++) {
                setOutputColor(data['tokenized_text'][i], data['highlighted_text'])
            }

        }).fail(function (data) {
            alert('error!');
        });


    });

});

/*
 This function takes in a word and the array of highlighted words and checks if the
 word matches any of the words in the highlighted words array.

 If it does it styles the word to be highlighted and appends it to the output text,
 if it doesn't, it styles the word normally and
 appends it to the output text.
 */
function setOutputColor(word, highlightedWords) {
    var highlight_flag = 0;
    for (var i = 0; i < highlightedWords.length; i++) {
        if (word == highlightedWords[i]) {
            var newSpan = null;
            newSpan = document.createElement('span');
            newSpan.setAttribute('class', 'highlighted-text');
            $('#original_text').append(newSpan);
            $(newSpan).text(word);
            highlight_flag = 1;
            break;
        }
    }

    var newSpan = null;
    newSpan = document.createElement('span');
    $('#original_text').append(newSpan);

    if (highlight_flag == 0) {
        $(newSpan).text(word + " ");
    } else {
        $(newSpan).text(" ");
    }


}


