// -*- encoding: utf-8 -*-
// Copyright (c) 2012, Daniel Barbeau Vasquez
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//     * Neither the name of Daniel Barbeau Vasquez nor the
//       names of its contributors may be used to endorse or promote products
//       derived from this software without specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
// ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
// WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
// DISCLAIMED. IN NO EVENT SHALL DANIEL BARBEAU VASQUEZ BE LIABLE FOR ANY
// DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
// (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
// LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
// ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

// Author: Daniel Barbeau Vasquez
// Contributors: -

//////////////////////////////////////////////////////////////////
// All the API loading stuff. Using callbacks to remain in-sync //
//////////////////////////////////////////////////////////////////


function load_google_api() {
    google.load("maps", "3", {callback: init_gmp, other_params : "sensor=false" });
}

function load_script(src, callback) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = src+"?callback="+callback;
    document.body.appendChild(script);
}


// The whole execution starts by this one called at the end of this file
function init_apis() {
    if (typeof google == "undefined") {
	load_script("https://www.google.com/jsapi", "load_google_api");
    }
    else {
	// meant to support multiple instances per page. currently this won't work
	init_gmp();
    }
}




///////////////////////////////
// Now we can initialise gmp //
///////////////////////////////

// This function is called after the google maps api is successfully loaded
function init_gmp() {	 
    console.error("This function should be overriden in the calling Django template");
    // The reason for this is that to call search_init we need some variables that must
    // be expanded via the template and that we do not want to have javascript templates
    // which would ruin user agent caching.
}

function gmp_init_end(gmp_conf) {

    // In the following section "markers" are localities retreived
    // from the django model, containing a name, an address and some
    // description. We refere to the "google.maps.Marker"s objects as 
    // "g_markers" or something similar.
    
    var map;
    var renderer;
    var geocoder = new google.maps.Geocoder();

    var g_markers      = {};
    var g_info_windows = [];

    function init_map() {
	geocoder.geocode( {address:gmp_conf.start_addr}, function (result, status) {
	    var map_options = {center:result[0].geometry.location,
			       mapTypeId: google.maps.MapTypeId.ROADMAP,
			       zoom: 8,
			      };
	    map = new google.maps.Map(document.getElementById(gmp_conf.map_element_id), map_options);

	    if (gmp_conf.draw_all_markers) {
		get_and_add_all_markers();
	    }
	});
    }
    
    ////////////////////////////////////
    // Marker manipulation comes next //
    ////////////////////////////////////
    function get_and_add_all_markers() {
	$.ajax( {
	    url:"/gmp/markers",
	    type:"GET",
	    data: {gmp_pk:gmp_conf.instance},
	    success: function(data, status, jqXHR) {			
		draw_markers(data.markers);
	    },
	    dataType: "json",
	    error: function(jqXHR, txt, error){alert(txt);},
	});
    }

    function draw_markers(markers) {
	for (var i=0; i < markers.length; i++) {
	    draw_marker(markers[i]);
	}
    }

    function draw_marker(marker) {
	geocoder.geocode( {address: marker.address}, function(result, status) {
	    var g_mark = create_g_marker(marker, result[0].geometry.location);
	    if (marker.text != null) {
		create_g_info_window(marker, g_mark);
	    }
	});
    }

    function clear_all_markers() {
	for (var i in g_markers) {
	    g_markers[i].setMap(null);
	    delete g_markers[i];
	    delete g_info_windows[i];
	}
	
    }

    function create_g_marker(marker, location) {
	var g_mark = new google.maps.Marker( {title:marker.name, 
					      position:location, 
					      map:map,
					      zIndex:google.maps.Marker.MAX_ZINDEX+1} );
	g_markers[marker.name] = g_mark;
	return g_mark;
    }

    function create_g_info_window(marker, g_marker) {
	var info_window = new google.maps.InfoWindow({content:marker.text});
	google.maps.event.addListener(g_marker, 'click', function() {
	    info_window.open(map, g_marker);
	});

	g_info_windows[marker.name] = info_window;	
	return info_window;
    }


    ////////////////////////////////////////
    // Closest marker functions come next //
    ////////////////////////////////////////
    function closest_request_handler(data, status, jqXHR) {
	function route_request_handler(dir_result, dir_status ) {
	    clear_all_markers();
	    draw_marker(data.closest);
	    renderer = new google.maps.DirectionsRenderer({directions:dir_result, map:map});
	}

	var directions = new google.maps.DirectionsService();
	directions.route( {travelMode:google.maps.TravelMode.DRIVING,
			   origin:data.origin,
			   destination:data.closest.address},
			  route_request_handler );
    }
    
    function bind_closest_marker_submit() {
	$("#closest_marker_form").submit( function(arg0, arg1, arg2){
	    var address = $("#address")[0];
	    var url = "/gmp/closest";
	    $.ajax( {
		url: url,
		type:"GET",
		data: $("#closest_marker_form").serialize(),
		success: closest_request_handler,
		dataType: "json",
	    });
	    return false; //== don't send the usual way since we do the AJAX thingy
	}
					);
    }

    bind_closest_marker_submit();
    init_map();
    
}



init_apis();
