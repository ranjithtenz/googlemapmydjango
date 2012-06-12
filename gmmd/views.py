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

from models import GoogleMapMyDjango
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, Http404

import json
import urllib



def gmp_from_request(post_or_get):
    if "gmp_pk" not in post_or_get:
        raise Http404    
    gmp_str = suspicious(post_or_get["gmp_pk"])
    if not gmp_str:
        return HttpResponseForbidden("Bad request 1")        
    gmp_pk = valid_gmp_pk(gmp_str)
    if not gmp_pk:
        return HttpResponseForbidden("Bad request 2")        
    return get_object_or_404(GoogleMapMyDjango, pk=gmp_pk)
    

@login_required
def get_fields_json(request):
    print "gets here"
    if not request.user.is_superuser:
        return HttpResponseForbidden("Forbidden")

    def make_dict(the_marker_model):
        return {"model_fields": [f.name for f in the_marker_model._meta.fields],
                "meta_model_fields": [f.name for f in GoogleMapMyDjango._meta.fields if f.name.startswith("f_")]}
        
    if request.GET:
        if "gmp_pk" in request.GET:
            gmp = gmp_from_request(request.GET)
            if gmp.m_marker:
                m_marker = gmp.m_marker.model_class()
                d = make_dict(m_marker)
            else:
                d = {}
        elif "modname" in request.GET:
            modname = suspicious(urllib.unquote_plus(request.GET["modname"]))
            if not modname:
                return HttpResponseForbidden("Bad request 3")
            m_marker = ContentType.objects.get(name= modname)
            if m_marker:
                m_marker = m_marker.model_class()
                d = make_dict(m_marker)
            else:
                d = {}
        else:
            d = {}

        response = HttpResponse(mimetype="application/json")
        response.write( json.dumps(d) )
        return response
            
    else:
        raise Http404


def get_markers_json(request):
    if request.GET:
        gmp = gmp_from_request(request.GET)
        
        if gmp.m_marker:
            m_marker = gmp.m_marker.model_class()
            json_marker = gmp.json_marker
            markers = [ json_marker(m) for m in m_marker.objects.all()]
            d = { "markers":markers }
        else:
            d = {}
    
        response = HttpResponse(mimetype="application/json")
        response.write( json.dumps(d) )
        return response
    else:
        raise Http404


def get_closest_marker_json(request):
    if request.GET:
        address = suspicious(request.GET["address"])
        if not address:
            return HttpResponseForbidden("Bad request 0")
        gmp = gmp_from_request(request.GET)
        marker  = gmp.closest_marker(address)
        response = HttpResponse(mimetype="application/json")
        response.write( json.dumps( { "closest": gmp.json_marker(marker), "origin":urllib.unquote_plus(address) } ) )
        return response
    else:
        raise Http404
    

def dump_request(request):
        response = HttpResponse(mimetype="text/plain")
        response.write( str(request.user)+"\n" )
        response.write( str(request.user.is_superuser)+"\n" )
        return response
    



###################################
# The begining of security checks #
###################################
def suspicious(string):
    return None if( "#" in string or ";" in string or ":" in string or "!" in string ) else string

def valid_gmp_pk(pk_str):
    try:
        pk = int(pk_str)
    except ValueError:
        return False
    else:
        return pk_str

    