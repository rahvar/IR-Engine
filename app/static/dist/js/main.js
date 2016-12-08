$(function(){    

    //////////////////////////// RESETS //////////////////////////////////////

    // All page resets
    function pageResets() {
        resetLangFilters();
        resetDateSlider();
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
    
    // Setting query into session when home button is pressed
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

    // Home location
    if(window.location.pathname == '/' || window.location.pathname == '') {
        sessionStorage.setItem('usrquery','');
        $("input[name='usrquery']").val('');
        pageResets();
    }

    /////////////////////////////////////////////////////////////////////////////////////

    // Setting date slider on page startup
    setDateSlider();

    // resetting date slider
    function resetDateSlider() {
        if(sessionStorage.getItem('dateSilderInfo') !== null)
            sessionStorage.removeItem('dateSilderInfo');
    }

    // Resetting the language filters
    function resetLangFilters() {
        // Resetting the language filters
        $('.lang-select').each(function(index, val) {
            $(this).prop('checked',false);
        });

        var checkboxvalues = JSON.parse(sessionStorage.getItem('checkboxvalues')) || {};
        for(var prop in checkboxvalues) {
            checkboxvalues[prop] = false;
        }
        sessionStorage.setItem('checkboxvalues',JSON.stringify(checkboxvalues));
    }

    // Resetting the date slider info
    function setDateSlider() {

        // Date Slider
        var dateInf = JSON.parse($('#datefromserver').text());

        var minDate = new Date(dateInf[0].y,dateInf[0].m-1,dateInf[0].d);
        var maxDate = new Date(dateInf[1].y,dateInf[1].m-1,dateInf[1].d);

        // set min and max date
        $("#dateSlider").dateRangeSlider({
            bounds:{
              min: minDate,
              max: maxDate
            },
            formatter:function(val){
            var days = val.getDate(),
                month = val.getMonth() + 1,
                year = val.getFullYear();
            return month + "-" + days + "-" + year%100;
          }
        });

        // If there was a search previously
        if(sessionStorage.getItem('dateSilderInfo') !== null) {

            var dateSilderInfo = JSON.parse(sessionStorage.getItem('dateSilderInfo'));
        
            console.log(dateSilderInfo)

            $("#dateSlider").dateRangeSlider("values", 
                new Date(dateSilderInfo['minDate']), 
                new Date(dateSilderInfo['maxDate']));               
        }
        else {
            // Set the date range slider 
            $("#dateSlider").dateRangeSlider("values",minDate,maxDate);
        }         
    }

    function dateFormat(minDate,maxDate) {

        // format - 2016-12-05T00:00:00Z

        var lMonth = parseInt(minDate.getMonth())+ 1;
        var uMonth = parseInt(maxDate.getMonth())+ 1;
        var lowerDate =  minDate.getFullYear() + '-' + lMonth+'-'+ minDate.getDate()+'T00:00:00Z';
        var upperDate =  maxDate.getFullYear() + '-' + uMonth + '-'+maxDate.getDate()+'T00:00:00Z';

        return {'minDate':lowerDate,'maxDate':upperDate};
    }

    // Date slider - triggered when the user changes the slider
    $("#dateSlider").bind("userValuesChanged", function(event, data){
        
        var dateSilderInfo = {};

        console.log("Something moved. min: " + data.values.min + " max: " + data.values.max);
        var minDate = data.values.min;
        var maxDate = data.values.max;

        dateSilderInfo['minDate'] = data.values.min;
        dateSilderInfo['maxDate'] = data.values.max;
        dateSilderInfo['fulldate'] = data.values;
        
        if(sessionStorage.getItem('dateSilderInfo') !== null)
            sessionStorage.removeItem('dateSilderInfo'); 

        sessionStorage.setItem('dateSilderInfo',JSON.stringify(dateSilderInfo));

        console.log("Inside userValuesChanged: " +  new Date(dateSilderInfo['minDate']) + dateSilderInfo['maxDate'])

        var date = dateFormat(minDate,maxDate);

        // Retrieve the query from the session
        var query = sessionStorage.getItem('usrquery');
    
        var uri = '/query?usrquery='+ query;
        uri += '&datefrom='+date['minDate']+'&dateto='+date['maxDate'];

        // Check language
        if(sessionStorage.getItem('checkboxvalues') !== null) {
            var checkboxvalues = JSON.parse(sessionStorage.getItem('checkboxvalues'));
            var lang = '';
            $.each(checkboxvalues, function(key, val) {
                if(key != '' && $('#'+key).prop('checked') == true)
                    lang += key + ' ' 
            });

            if(lang != '')
                uri += '&lang=' + lang;
        }

        window.location.assign(uri)
    });

    /////////////////////////////////// TAGS /////////////////////////////////////////

    // To populate tags from server
    $.ajax({
        url: "/tags",
        method: "POST",
        dataType: "json"
    })
    .done(function(data) {
        console.log("success");
        for(var i = 0; i < data.length; i+=2) {
            if(data[i+1] < 100)
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

    /////////////////////////////////// PAGINATION /////////////////////////////////////////

    // Pagination
    var perPage = $('.paginate');
    // total num of tweets 
    var totNumTweets = perPage.length;
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

    /////////////////////////////////// LANGUAGE FACETING ///////////////////////////////////////

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

        if(sessionStorage.getItem('dateSilderInfo') !== null) {

            var dateSliderInfo = JSON.parse(sessionStorage.getItem('dateSilderInfo'));
            uri += '&datefrom='+dateSliderInfo['minDate']+'&dateto='+ dateSliderInfo['maxDate'];
        }

        //alert(uri)     
        window.location.assign(uri) 
    }); 

    /////////////////////////////////// DETECT LANGUAGE ///////////////////////////////////////


	//Detect language from search bar
    $('.search-bar').keydown(function(e)
	{
    	var keycode1 = (e.keyCode ? e.keyCode : e.which);
    	if (keycode1 == 8)
    		return;
    	
        var query_text = $('.search-bar').val();
        if (query_text.split(' ').length > 2)
    	{
            $.ajax(
    		{
                url: "/getLang",
                method: "GET",
                dataType: "json",
                data: {query:query_text},
            })
            .done(function(data)
    		{
            	var lang_map = {'english':'en','spanish':'es','portuguese':'pt','french':'fr'}
            	var languages = ['english','spanish','portuguese','french'];
            	//console.log(data);
            	if (languages.indexOf(data.language)<0)
        		{
            		data.language='english';
            		//console.log(lang_map[data.language]);
        		}
        		$('.lang-select').val(lang_map[data.language]);
            })
            .fail(function() 
    		{
                //console.log("error");
            })
		}
	});

    /////////////////////////////////// MAPS ///////////////////////////////////////


});