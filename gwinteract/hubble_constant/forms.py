from django import forms
from django.contrib.postgres.forms import SimpleArrayField

from ligo.org import request

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Field
from crispy_forms.bootstrap import Div

from ligo.gracedb.rest import GraceDb

import json
import re

api="https://gracedb-playground.ligo.org/api/"

class HubbleConstantForm(forms.Form): 
    def __init__(self, *args, **kwargs):
        super(HubbleConstantForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = '/hubble-constant/hubble-constant/'
        self.helper.form_method = 'GET'
        self.helper.form_id = 'hubble_form'
        self.helper.layout = Layout(
            Fieldset("Select SkyMaps and Redshifts",
                Field('gids',),
                Field('event_skymaps',),
                Field('event_redshifts'),
            ),
            Fieldset("Manual Over Rides",
                Row(
                Field('manual_redshift', css_class='form-group col-md-6 mb-0'),
                Field('manual_redshift_uncertainity', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
                ),
            ),
            Fieldset("Prior",
                Row(
                    Column('priors', css_class='form-group col-md-4 mb-0'), 
                    Column('hmin', css_class='form-group col-md-4 mb-0'),
                    Column('hmax', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset("Cosmology",
                Row(
                    Column('H_O', css_class='form-group col-md-6 mb-0'),
                    Column('omega_m', css_class='form-group col-md-6 mb-0'),
                    Column('H_O_res', css_class='form-group col-md-6 mb-0'),
                    Column('zres', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('submit', 'Generate Hubble Constant')
        )

    response = json.loads(request('https://ldas-jobs.ligo.caltech.edu/~maya.fishbach/H0_calculator/GID_list.json', use_kerberos=True))

    GID_CHOICES = tuple(zip(list(response.values())[0], list(response.values())[0]))

    connection = GraceDb(api)
    ALL_MAPS_NAMES = []
    ALL_GALAXIES = []
    filter_out_commas = re.compile("^[^,]+$")
    filter_skymaps = re.compile(".*fits")
    filter_galaxy = re.compile("galaxy")
    for gid in list(response.values())[0]:
        files_associated_with_event = connection.files(gid).json()
        files_no_comma  = list(filter(filter_out_commas.match, files_associated_with_event.keys()))
        skymaps = list(filter(filter_skymaps.match, files_no_comma))
        for name in skymaps:
            ALL_MAPS_NAMES.append(gid + '-' + name)
        galaxies = list(filter(filter_galaxy.match, files_no_comma))
        for name in galaxies:
            ALL_GALAXIES.append(gid + '-' + name)

    SKYMAP_CHOICES = tuple(zip(ALL_MAPS_NAMES, ALL_MAPS_NAMES))
    REDSHIFT_CHOICES = tuple(zip(ALL_GALAXIES, ALL_GALAXIES))

    FLAT_PRIOR = 'flat_prior'
    LOG_PRIOR = 'log_prior'
    PRIOR_CHOICES = (
        (FLAT_PRIOR, 'flat prior'),
        (LOG_PRIOR, 'log prior'),
    )

    gids = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        choices=GID_CHOICES,
    )

    # H0 priors
    priors = forms.ChoiceField(choices=PRIOR_CHOICES,)
    hmin = forms.FloatField()
    hmax = forms.FloatField()

    event_skymaps = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=SKYMAP_CHOICES,
    )

    event_redshifts = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        choices=REDSHIFT_CHOICES,
    )

    manual_redshift = forms.FloatField()
    manual_redshift_uncertainity = forms.FloatField()

    # COSMOLOGY
    H_O = forms.FloatField(label="default H0 value to use in defining cosmology functions in km/s/Mpc")
    omega_m = forms.FloatField(label='Omega_m,0 to use in cosmology functions')
    H_O_res = forms.FloatField(label='resolution to use when computing H0 posterior in km/s/Mpc')
    zres = forms.FloatField(label='resolution in redshift to define dL-z linear interpolant')

class HubbleConstantPlotForm(forms.Form):
    hs = SimpleArrayField(forms.FloatField())    
    ho_likelihood = SimpleArrayField(forms.FloatField()) 

class HubbleConstantJSONForm(forms.Form):
    hs = SimpleArrayField(forms.FloatField())
    ho_likelihood = SimpleArrayField(forms.FloatField())
