/**
 * Created by rodriga on 1/12/2015.
 */
$(function () {

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
                '       <button type="button" class="btn btn-primary btn-next" id="submit"><i class="glyphicon glyphicon-upload"></i> Upload</button>\n' +
                '   </div>\n' +
                '</div>'
        }
    });

    $("#submit").click(function () {

        var form_data = new FormData($('#uploadform')[0]);
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
            var outputHtml = document.createElement('div');
            outputHtml.innerHTML = '<center><h1>Abstract #<span id="abstract_id"></span></h1></center><br><div class="row"> <div class="col-lg-6"><div class="panel panel-default"><div class="panel-heading"><center><h3 class="panel-title">Summary</h3></center></div><div class = "panel-body"><center><span id="hashtags2"></span></center></div></div></div><div class="col-lg-6"><div class="panel panel-default"><div class="panel-heading"><center><h3 class="panel-title">Original Abstract</h3></center></div><div class="panel-body"><div id="original_text"></div></div></div></div></div>'
            for (var i = 0; i
                < data['fileInfo'].length; i++) {
                var outputBlock = outputHtml.cloneNode(true);
                var outputHeader = outputBlock.childNodes;
                var outputTitle = outputHeader[0].childNodes;
                var outputId = outputTitle[0].childNodes;

                outputId.item(1).textContent = data['fileInfo'][i]['abstract_id'];
                var outputRow = outputHeader[2].childNodes;


                var outputCol1 = outputRow[1].childNodes;
                var summaryPanel = outputCol1[0].childNodes;

                var summaryPanelBody = summaryPanel[1].childNodes;
                summaryPanelBody.item(0).textContent = data['fileInfo'][i]['hashtags'];
                var outputCol2 = outputRow[2].childNodes;
                var outputPanel = outputCol2[0].childNodes;
                var outputPanelBody = outputPanel[1].childNodes;


                for (var j = 0; j < data['fileInfo'][i]['tokenized_text'].length; j++) {
                    setOutputColor(data['fileInfo'][i]['tokenized_text'][j], data['fileInfo'][i]['highlighted_text'], outputPanelBody.item(0))
                }
                $('#output').append(outputBlock);


            }
            $('#myWizard').wizard('next');


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


