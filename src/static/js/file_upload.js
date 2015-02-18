/**
* Created by rodriga on 1/12/2015.
*/
$(function () {

    /* Setup file uploader*/
    $("#input-700").fileinput({
        dropZoneEnabled: false,
        layoutTemplates: {
            main1: '{preview}\n' +
                '<div class="kv-upload-progress hide"></div>\n' +
                '<div class="input-group {class}">\n' +
                '   {caption}\n' +
                '   <div class="input-group-btn">\n' +
                '       {remove}\n' +
                '       {cancel}\n' +
                '       {browse}\n' +
                '       <button type="button" class="btn btn-primary btn-next kv-fileinput-upload" id="submit"><i class="glyphicon glyphicon-upload"></i> Upload</button>\n' +
                '   </div>\n' +
                '</div>'
        }
    });

    /* Process uploaded files when user clicks the upload button*/
    $("#submit").click(function () {

        var form_data = new FormData($('#uploadform')[0])

        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            processData: false,
            cache: false,
            async: false,
            dataType: 'json'
        }).done(function (data) {

            /* The code below creates the uploaded files table and populates it with the information necessary*/
            for (var i = 0; i < data['fileInfo'].length; i++) {
                var fileRow = document.createElement('tr');
                var fileID = document.createElement('td');
                var fileName = document.createElement('td');
                var fileLink = document.createElement('td');
                fileID.textContent = data['fileInfo'][i]['abstract_id'];
                fileName.textContent = data['fileInfo'][i]['filename'];
                fileLink.innerHTML = '<a href="' + data['fileInfo'][i]['abstract_id'] + '"> View Summary </a>';
                fileRow.appendChild(fileID);
                fileRow.appendChild(fileName);
                fileRow.appendChild(fileLink);
                $('#fileList').append(fileRow);
                createOutput(data, i);

            }

            /* Automatically move the wizard to the next step to see the table*/
            $('#myWizard').wizard('next');

            /* creates the output files when the user clicks 'next' on the second step of the wizard*/
            $('#results').click(function () {
                for (var i = 0; i < data['fileInfo'].length; i++) {
                    var resultsFileLink = document.createElement('span');
                    resultsFileLink.innerHTML = '<a href="downloads/' + data['fileInfo'][i]['abstract_id'] + '"> Results for <span id="original_filename"></span></a><br>';
                    resultsFileLink.childNodes.item(0).childNodes.item(1).textContent = data['fileInfo'][i]['filename'];
                    $('#resultsList').append(resultsFileLink);
                }
                /* Move to the last step of the wizard when the next button is clicked*/
                $('#myWizard').wizard('next');
            })
        }).fail(function (data) {
            alert('error!');
        });


    });


});

function createOutput(data, index) {
    $('#hashtags').text(data['fileInfo'][index]['hashtags']);
    $('#abstract_id').text(data['fileInfo'][index]['abstract_id']);

    for (var i = 0; i < data['fileInfo'][index]['tokenized_text'].length; i++) {
        setOutputColor(data['fileInfo'][index]['tokenized_text'][i], data['fileInfo'][index]['highlighted_text'])
    }
}
/*
This function takes in a word and the array of highlighted words and checks if the
word matches any of the words in the highlighted words array.

If it does it styles the word to be highlighted and appends it to the output text,
if it doesn't, it styles the word normally and
appends it to the output text.
*/
function setOutputColor(word, highlightedWords, span) {
    var highlight_flag = 0;
    for (var i = 0; i < highlightedWords.length; i++) {
        if (word == highlightedWords[i]) {
            var newSpan = null;
            newSpan = document.createElement('span');
            newSpan.setAttribute('class', 'highlighted-text');
            $(span).append(newSpan);
            $(newSpan).text(word);
            highlight_flag = 1;
            break;
        }
    }

    var newSpan = null;
    newSpan = document.createElement('span');
    $(span).append(newSpan);

    if (highlight_flag == 0) {
        $(newSpan).text(word + " ");
    } else {
        $(newSpan).text(" ");
    }


}