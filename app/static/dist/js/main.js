$(function(){    

    // Setting date slider on page startup
    setDateSlider();

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

    // resetting date slider
    function resetDateSlider() {
        if(sessionStorage.getItem('dateSilderInfo') !== null)
            sessionStorage.removeItem('dateSilderInfo');
    }

    // Resetting the date slider info
    function setDateSlider() {

        var dateInf = JSON.parse($('#datefromserver').text());

        $("#dateSlider").dateRangeSlider({
            bounds:{
              min: new Date(dateInf[0].y,dateInf[0].m-1,dateInf[0].d),
              max: new Date(dateInf[1].y,dateInf[1].m-1,dateInf[1].d)
            }
        });

        if(sessionStorage.getItem('dateSilderInfo') !== null) {

            var dateSilderInfo = JSON.parse(sessionStorage.getItem('dateSilderInfo'));
        
            console.log(dateSilderInfo)

            $("#dateSlider").dateRangeSlider("values", 
                new Date(dateSilderInfo['minDate']), 
                new Date(dateSilderInfo['maxDate']));               
        }            
    }

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

        // if(sessionStorage.getItem('dateSilderInfo') != null) 
        //     uri += 

        //alert(uri)
        window.location.assign(uri) 
    });

    // reinstate the previous state from session
    // if(sessionStorage.getItem('dateSilderInfo') != null) {  

    //     var dateSilderInfo = JSON.parse(sessionStorage.getItem('dateSilderInfo'));

    //     $("#dateSlider").dateRangeSlider({
    //       bounds:{
    //         min: dateSilderInfo['minDate'],
    //         max: dateSilderInfo['maxDate']
    //     }});
    // }    

    // Date slider 
    $("#dateSlider").bind("userValuesChanged", function(event, data){
        
        var dateSilderInfo = {};

        console.log("Something moved. min: " + data.values.min + " max: " + data.values.max);
        var minDate = data.values.min;
        var maxDate = data.values.max;

        dateSilderInfo['minDate'] = data.values.min;
        dateSilderInfo['maxDate'] = data.values.max;
        dateSilderInfo['fulldate'] = data.values;

        // Check if its same date in the session
        // if (sessionStorage.getItem('dateSilderInfo') !== null) {
        //     var dateSilderInfo = JSON.parse(sessionStorage.getItem('dateSilderInfo'));
        //     var startDate = dateSilderInfo['minDate'];
        //     var endDate = dateSilderInfo['maxDate'];

        //     if(startDate == minDate && endDate == maxDate) {
        //         event.preventDefault();
        //     }
        // }
       
        // Store the date in session

        
        if(sessionStorage.getItem('dateSilderInfo') !== null)
            sessionStorage.removeItem('dateSilderInfo'); 

        sessionStorage.setItem('dateSilderInfo',JSON.stringify(dateSilderInfo));

        console.log("Inside userValuesChanged: " +  new Date(dateSilderInfo['minDate']) + dateSilderInfo['maxDate'])


        // format - 2016-12-05T00:00:00Z
        var lMonth = parseInt(minDate.getMonth())+ 1;
        var uMonth = parseInt(maxDate.getMonth())+ 1;
        var lowerDate =  minDate.getFullYear() + '-' + lMonth+'-'+ minDate.getDate()+'T00:00:00Z';
        var upperDate =  maxDate.getFullYear() + '-' + uMonth + '-'+maxDate.getDate()+'T00:00:00Z';

        console.log(lowerDate);
        console.log(upperDate);
        
        // Retrieve the query from the session
        var query = sessionStorage.getItem('usrquery');
    
        var uri = '/query?usrquery='+ query;
        uri += '&datefrom='+lowerDate+'&dateto='+upperDate;

        window.location.assign(uri)
    });


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



    // Maps
    var map;
    function initMap() {

        map = new google.maps.Map(document.getElementById('map'), {
          zoom: 8 ,
          center: {lat: -28.024, lng: 140.887}
        });

        // Create an array of alphabetical characters used to label the markers.
        var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

        // Add some markers to the map.
        // Note: The code uses the JavaScript Array.prototype.map() method to
        // create an array of markers based on a given "locations" array.
        // The map() method here has nothing to do with the Google Maps API.
        // var markers = locations.map(function(location, i) {
        //   return new google.maps.Marker({
        //     position: location,
        //     label: labels[i % labels.length]
        //   });
        // });

        // Add a marker clusterer to manage the markers.
    //     var markerCluster = new MarkerClusterer(map, markers,
    //         { imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
    // 
    }


    google.maps.event.addDomListener(window, 'load', initMap);

    $('#myModal').on('shown.bs.modal', function () {
        google.maps.event.trigger(map, "resize");
    });

});
