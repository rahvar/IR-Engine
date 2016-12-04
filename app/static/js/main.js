$(function(){    

    // Resetting the language filters
    function resetLangFilters() {
        // Resetting the language filters
        $('.lang-select').each(function(index, val) {
            $(this).prop('checked',false);
        });
    }

    // All page resets
    function pageResets() {
        resetLangFilters();
    }

    // Setting the query into session when submitting
    $('#user-search').submit(function(event) {
        var user_query = $("input[name='usrquery']").val();
        sessionStorage.setItem('usrquery',user_query);
        //alert("Setting to storage: " + sessionStorage.getItem('usrquery'))
        pageResets();
    });

    // Setting the query into session when submitting from tags
    $('.trending-tags').on('click', '.tag-item', function(event) {
        var query = $(this).attr('data-qtext');
        sessionStorage.setItem('usrquery',query);
        pageResets();
    });
    
    // Setting query into sessio when home button is pressed
    $('.home-btn').click(function(event) {
        sessionStorage.setItem('usrquery','');
        pageResets();

        // Resetting the lang selectors in session to empty 
        sessionStorage.removeItem('checkboxvalues')
    });

    // Setting search bar field with the previous search from session
    if(sessionStorage.getItem('usrquery') !== null) {
       $("input[name='usrquery']").val(sessionStorage.getItem('usrquery'));
    }
    else {
        sessionStorage.setItem('usrquery','');
    }

    // To populate tags from server
    $.ajax({
        url: "/tags",
        method: "POST",
        dataType: "json"
    })
    .done(function(data) {
        console.log("success");
        //console.log(data)
        for(var i = 0; i < data.length; i+=2) {
            if(data[i+1] < 3)
                break
            $('.trending-tags').append(
                            "<a href=\""
                            + "/query?usrquery=" + data[i] + "\""
                            + "class=\"list-group-item tag-item\" data-qtext=\""+ data[i] +"\">"
                            + "<i class=\"fa fa-hashtag fa-fw\"></i>"
                            +  data[i]
                            + "<span class=\"pull-right text-muted small\"><em>" 
                            +  data[i+1]
                            + "</em> </span> </a>")
        }

    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        console.log("complete");
    });      


    // Pagination
    var perPage = $('.paginate');
    // total num of tweets 
    var totNumTweets = perPage.length;
    console.log("Total num tweets: "+totNumTweets);
    // num of tweets at a time 
    var perPageTweets = 5;
    // When the document loads hide everything else besides the first 5
    perPage.slice(perPageTweets).hide();
    // Applying pagination
    $('#page-nav').pagination({
        items: totNumTweets,
        itemsOnPage: perPageTweets,
        //cssStyle: 'light-theme',
        onPageClick: function(pageNum) {
            var start = perPageTweets * (pageNum - 1);
            var end = start + perPageTweets;

            // First hide all page parts
            // Then show those just for our page
            perPage.hide().slice(start, end).show();
        }
    });

    // lang-select on page load
    var checkboxvalues = JSON.parse(sessionStorage.getItem('checkboxvalues')) || {};
    //var $checkboxes = $("#langs :checkbox");

    // reinstate checkbox status from session
    $.each(checkboxvalues, function(key, val) {
        if(key != '')
            $('#'+key).prop('checked',val);  
    });

    // lang-select triggered when lang is selected
    $('#langs').change(function(event) {
        
        var langs_selected = ''
        var url, query;

        // Iterate through each checkbox and read its status
        $('.lang-select').each(function(index, val) {
            if($(this).is(':checked')) {
                if(langs_selected != '')
                    langs_selected += ' ' + $(this).attr('value');
                else
                    langs_selected = $(this).attr('value');
            }
            // saving checked status in an object
            checkboxvalues[this.id] = this.checked;
        });

        // saving the checked status to session object
        sessionStorage.setItem('checkboxvalues',JSON.stringify(checkboxvalues));

        // retrieving the query from the session
        query = sessionStorage.getItem('usrquery');

        var uri = '/query?usrquery='+ query

        // Setting the language filter
        if (langs_selected != '') {
            uri += '&lang=' + langs_selected;
        }
        //alert(uri)
        window.location.assign(uri) 
    });

});