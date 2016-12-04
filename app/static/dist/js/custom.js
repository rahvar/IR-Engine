$(function()
{
    // To populate tags
    $.ajax({
        url: "/tags",
        method: "POST",
        dataType: "json"
    })
    .done(function(data) {
        console.log("success");
        for(var i = 0; i < data.length; i+=2) {
            if(data[i+1] < 3)
                break
            $('.trending-tags').append(
                            "<a href=\""
                            + "/query?usrquery=" + data[i] + "\""
                            + "class=\"list-group-item\">"
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

	//Detect language from search bar
    $('.search-bar').keydown(function(e)
	{
    	var keycode1 = (e.keyCode ? e.keyCode : e.which);
    	if (keycode1 == 8)
    		return;
    	
//        if (keycode1 == 0 || keycode1 == 9) 
//        {
//        	$('.search-bar').css({background:'yellow'});
//            e.preventDefault();
//            e.stopPropagation();
//        }
    	
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
            	console.log(data);
            	if (languages.indexOf(data.language)<0)
        		{
            		data.language='english';
            		console.log(lang_map[data.language]);
        		}
        		$('.lang-select').val(lang_map[data.language]);
        		$('#query_tags').empty();
        		if(data.entities[0].hasOwnProperty('disambiguated') && data.entities[0].disambiguated.hasOwnProperty('subType'))
    			{
        			tags = data.entities[0].disambiguated.subType;
        			console.log(tags);
        			length = tags.length < 7 ? tags.length : 7;
        			for(i=0;i<length;i++)
    				{
        				var span = $('#query_tags').append('<span>'+tags[i]+'</span>&nbsp;&nbsp;');
    				}
        			
    			}
            })
            .fail(function() 
    		{
                console.log("error");
            })
		}
	});
    
    /*$(window).load(function()
	{*/
		$('.Collage').collagePlus
		 ({
			 /*
			* The ideal height you want your row to be. It won't set it exactly to this as
			* plugin adjusts the row height to get the correct width
			*/
			'targetHeight'    : 500,
			'effect' : "effect-4",
			   /*
			* vertical: effects applied per row to give the impression of descending appearance
			* horizontal: effects applied in order of appearance in the row to give a horizontal appearance
			*/
			   'direction'       : 'horizontal',
			
			   /*
			   * Sometimes there is just one image on the last row and it gets blown up to a huge size to fit the
			   * parent div width. To stop this behaviour, set this to true
			   */
			   'allowPartialLastRow'       : false
		 });
	//});

	$('#search-form').submit(function()
	{
		var query_text = $('.search-bar').val();
		$.ajax({
	        url: "/query",
	        method: "GET",
	        dataType: "json",
	        data: {query:query_text},
	    })
	    .done(function(data)
	    {
	    	console.log(data.tweets);
	    	for(tweet in data.tweets)
    		{
	    		console.log(tweet);
	    		var t_html = tweet.html[0];
	    		$('#tweet-body').append(
	    		'<div class="qa-message-list">\
	                <div class="message-item">\
	                    <div class="qa-message-content">'+ t_html +'</div>\
	                </div>\
	            </div>')
    		}
	    		
	    })
	    .fail(function(data)
		{
	    	console.log("fail");
		});
	});
});

