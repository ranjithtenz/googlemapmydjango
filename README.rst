GoogleMapMyDjango
=================
(short name : gmmd)


A simple django-cms plugin to dig data from a model and place it on a google map. For example, you have
a Django model that describes Users and where they live:

.. code::
    :class: python

    from django.db import models
    class User(models.Model):
	first_name       = models.CharField( _(u"Your first name"), max_length=50)
	last_name        = models.CharField( _(u"Your family name"), max_length=50)
	address          = models.CharField( _(u"Where you live"), max_length=200)


Then you can show their homes on a google map by telling GoogleMapMyDjango to look into the User model, and
to use the "address" field to plot the markers on the map. All the hard work is done by Google so say "thank you Google".


Features
--------

 * Plot your point data on a GoogleMap with an optionnal InfoWindow
 * Find your point data that is the closest to anywhere + routing.
    

Installation
------------

.. code:: 
    :class: bash

    git clone git://github.com/dbarbeau/googlemapmydjango.git
    cd googlemapmydjango
    python setup.py install


Then:

 * add "gmmd" to "INSTALLED_APPS" in your project's settings.py
 * add url(r"^gmp/", include('gmmd.urls')) to your project's urls.py


Configuration
-------------

Add an instance of the gmmd plugin to one of your pages in your administration interface.
Next we describe the available fields:

 * **Title** : The title of the map (currently undisplayed)
 * **Map Element Id** : The id name to use for the <div> element in the page. Change this if there is an id conflict. Cannot be blank!
 * **Map location** : A full text address to center the map on initialisation, eg: "Paris, Texas, USA".
 * **M marker** : Name of the model in which gmmd will dig for the data (eg: the "user" model from the above example)
 * **Marker Model Pk Field** : Primary key field name in the M marker model (currently unused, leave blank)
 * **Marker Model Title Field** : Name of the field that contains the name of the marker (str, optionnal).
 * **Marker Model Geocode Field** : Name of the field that contains the address of the data to plot (str, required).
 * **Marker Model InfoWindow Content Field** : Name of the field that contains the text to show in the InfoWindow. If blank, no InfoWindow will be displayed  (str, optionnal).
 * **Enable closest search panel** : If checked, will display a form to search for closest marker to whatever address is entered.
 * **Finder Text** : A description to display next to the search box
 * **Finder button Text** : A short text to display in the search button
 * **Cache search results** : If checked, the closest marker to a place will be stored to speed up same requests.





