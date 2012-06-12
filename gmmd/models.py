# -*- encoding: utf-8 -*-
# Copyright (c) 2012, Daniel Barbeau Vasquez
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Daniel Barbeau Vasquez nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL DANIEL BARBEAU VASQUEZ BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Daniel Barbeau Vasquez
# Contributors: -

from django.contrib.contenttypes.models import ContentType
from cms.models.pluginmodel import CMSPlugin
from django.utils.translation import ugettext_lazy as _
from django.db import models

import json
import urllib
import urllib2

# Create your models here.
class GoogleMapMyDjango(CMSPlugin):
    title = models.CharField( _(u"Title"), max_length=100 )

    map_element_id = models.CharField( _(u"Map Element Id"), max_length=100, default="gmmd_map_result")
    initial_address = models.CharField( _(u"Map location"), max_length=100 )

    # Which model should we take markers from
    m_marker = models.ForeignKey(ContentType, null=True, blank=True)

    # If true and m_marker is not null we draw all markers
    draw_all_markers = models.BooleanField( _(u"Draw all markers")  )
    # Which field from m_marker contains the primary key
    f_marker_pk = models.CharField( _(u"Marker Model Pk Field"), max_length=30, blank=True)
    # Which field from m_marker contains the marker name
    f_marker_title = models.CharField( _(u"Marker Model Title Field"), max_length=30, blank=True)
    # Which field from m_marker contains the marker's address
    f_marker_address = models.CharField( _(u"Marker Model Geocode Field"), max_length=30, blank=True)
    # Which field from m_marker contains info_window content
    f_info_window_content = models.CharField( _(u"Marker Model InfoWindow Content Field "), max_length=30, blank=True)

    # If true and m_marker is not null we enable closest marker search and routing.
    closest_finder = models.BooleanField( _(u"Enable closest search panel") )
    # Text to display close to the finder form
    closest_finder_text = models.CharField( _(u"Finder text"), max_length=100, blank=True, null=True, 
                                            default=_(u"Enter your locality (eg: Boulevard Haussman, Paris, France) "+ \
                                                      u"to find the closest shop to your place.") )
    find_button_text = models.CharField( _(u"Find button text"), max_length=20, blank=True, null=True, 
                                         default=_(u"Find!") )

    # If True, caches closest search results
    cache_results  = models.BooleanField( _(u"Cache search results"), default=True )

    def __unicode__(self):
        return "GoogleMapMyDjango "+self.title
    
    def copy_relations(self, oldinstance):
        self.m_marker = oldinstance.m_marker

    def json_marker(self, marker):            
        """ Generate a JSON marker factory. This is for speed reasons
        to prevent too many accesses through "." """
        
        addr_field = self.f_marker_address
        titl_field = self.f_marker_title
        info_field = self.f_info_window_content

        def json_marker( marker ) :
            if not marker:
                return None
            return {"address":getattr(marker, addr_field) if addr_field else "",
                    "name"   :getattr(marker, titl_field) if titl_field else "No title",
                    "text"   :getattr(marker, info_field) if info_field else None }

        self.json_marker = json_marker
        return json_marker(marker)
        
    def closest_marker(self, address):
        use_cache = self.cache_results
        cclosest  = ClosestMarkerCache.objects.get_or_create(address = address)[0] if use_cache else None
        if cclosest and cclosest.marker:
            #cclosest.marker is the key 
            return self.m_marker.model_class().objects.get(pk=cclosest.marker)
        else:
            # We don't have it, so compute the closest
            all_markers = self.m_marker.model_class().objects.all()

            marker_addr = self.f_marker_address
            def d_cmp(x,y):
                return cmp( google_distance(address, getattr(x, marker_addr)),
                            google_distance(address, getattr(y, marker_addr))  )

            sortd_sales = sorted(all_markers, cmp=d_cmp)

            if len(sortd_sales):
                marker = sortd_sales[0]
                if use_cache:
                    cclosest.marker = marker
                    cclosest.save()
                return marker
            else:
                return None


    class Meta:
        verbose_name_plural = "Google Maps Pluses"



# It is a cache to avoid too many google queries.
class ClosestMarkerCache(models.Model):
    address = models.CharField( _(u"User address"), max_length=256, primary_key=True)
    marker  = models.CharField( _(u"Marker pk"), max_length=256, null=True, blank=True, default=None)

    def __unicode__(self):
        return self.address



gurl = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&sensor=false"
def google_distance(address_a, address_b):
    # TODO_SECURITY : make sure address_a and address_b are safe!
    url = urllib.quote_plus(gurl%(address_a,address_b), safe=":/?&=")
    google_connection = urllib2.urlopen( url, timeout=3 )
    geocode_txt       = google_connection.read()
    google_connection.close()
    # the result should be a 1x1 matrix, and value is in meters
    return json.loads(geocode_txt)["rows"][0]["elements"][0]["distance"]["value"]    

