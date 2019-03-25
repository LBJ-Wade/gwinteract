# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
from .forms import HubbleConstantForm, HubbleConstantPlotForm, HubbleConstantJSONForm
from django.shortcuts import render
from ligo.org import request
from django.conf import settings
from ligo.gracedb.rest import GraceDb
from gwcosmology.ho import measure_H0_from_skymap
from six.moves import urllib

from matplotlib import use
use('agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import os
import io
import json
import seaborn
import h5py
import numpy
import math

_defaults = {'manual_redshift' : 0.0, 'priors' : 'flat_prior', 'manual_redshift_uncertainity' : 0.0,
             'hmin' : 20.0, 'hmax' : 200.0, 'H_O' : 70.0, 'H_O_res' : 1.0, 'zres' : 0.0005,
             'omega_m' : 0.3}

API="https://gracedb-playground.ligo.org/api/"

# Create your views here.
def index(request):
    form = HubbleConstantForm(_defaults)
    return render(request, 'hubble-constant-form.html', {'form': form})

def hubble_constant(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':

        # create a form instance and populate it with data from the request:
        form = HubbleConstantForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            hs, ho_likelihood = calculate_ho(form)

            plot_url_base = request.get_full_path()[::-1].replace('hubble-constant'[::-1], 'plot'[::-1], 1)[::-1].split('?')[0]
            json_url_base = request.get_full_path()[::-1].replace('hubble-constant'[::-1], 'json'[::-1], 1)[::-1].split('?')[0]

            parts = {
                'hs': ','.join(hs.astype(str).tolist()),
                'ho_likelihood': ','.join(ho_likelihood.astype(str).tolist()),
            }

            search = urllib.parse.urlencode(parts)

            ploturl = '{}?{}'.format(plot_url_base, search)
            jsonurl = '{}?{}'.format(json_url_base, search)

            return render(request, 'hubble-constant-results.html',
                          {'ploturl' : ploturl, 'jsonurl' : jsonurl}
                          )

        else:
            return render(request, 'hubble-constant-form.html', {'form': form})

def plot_ho(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':

        # create a form instance and populate it with data from the request:
        form = HubbleConstantPlotForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            hs = form.cleaned_data["hs"]
            ho_likelihood = form.cleaned_data["ho_likelihood"]
            
            with seaborn.axes_style('white'):
                ax = seaborn.distplot(hs, hist_kws={'weights': ho_likelihood}, kde=False,  rug=True, bins=int(math.sqrt(len(hs))))

            ax.set_xlim([min(hs), max(hs)])
            fig = ax.get_figure()
            canvas = FigureCanvas(fig)

            buf = io.BytesIO()
            canvas.print_png(buf)
            response=HttpResponse(buf.getvalue(),content_type='image/png')
            fig.clear()
            return response

def ho_json(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':

        # create a form instance and populate it with data from the request:
        form = HubbleConstantJSONForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            hs = form.cleaned_data["hs"]
            ho_likelihood = form.cleaned_data["ho_likelihood"]

            return JsonResponse({'H0_start': hs[0], 'dH0': hs[1]-hs[0], 'num_H0': len(hs), 'H0_likelihood': ho_likelihood}) 

def calculate_ho(form):
    events = form.cleaned_data["gids"]
    event_redshifts = form.cleaned_data["event_redshifts"]
    event_skymaps = form.cleaned_data["event_skymaps"]
    hmin = form.cleaned_data["hmin"]
    hmax = form.cleaned_data["hmax"]
    Ho_def = form.cleaned_data["H_O"]
    Ho_res = form.cleaned_data["H_O_res"]
    zres = form.cleaned_data["zres"]
    omega_m = form.cleaned_data["omega_m"]

    paths_to_redshifts, paths_to_skymaps = obtain_files(event_redshifts, event_skymaps)

    ho_likelihood_all = numpy.ones(numpy.arange(hmin, hmax, Ho_res).size)
    for redshift, skymap in zip(sorted(paths_to_redshifts), sorted(paths_to_skymaps)):
        with open(redshift) as data_file:
            galaxy = json.load(data_file)
        z_mean = galaxy['z']
        z_std = galaxy['sigma']
        ra = galaxy['RA']
        dec = galaxy['DEC']
        name = galaxy['name']
        hs, lh = measure_H0_from_skymap(skymap, z_mean, z_std, ra, dec, omega_m, Ho_def, zres, hmin, hmax, Ho_res)
        ho_likelihood_all *= lh

    return hs, ho_likelihood_all

def obtain_files(event_redshifts, event_skymaps):
    client = GraceDb(API)
    paths_to_redshifts = []
    paths_to_skymaps = []
    for redshift_file in event_redshifts:
        gid = redshift_file.split('-')[0]
        # strip off gid
        redshift_file = redshift_file.replace(gid + '-', '', 1)
        directory = os.path.join(settings.MEDIA_ROOT, 'files', 'redshift', gid,)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        path = os.path.join(directory, redshift_file)
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(client.files(gid, '{0}'.format(redshift_file)).read())
        paths_to_redshifts.append(path)

    for skymap_file in event_skymaps:
        gid = skymap_file.split('-')[0]
        skymap_file = skymap_file.replace(gid + '-', '', 1)
        directory = os.path.join(settings.MEDIA_ROOT, 'files', 'skymaps', gid,)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        path = os.path.join(directory, skymap_file)
        if not os.path.isfile(path):
            with open(path, 'wb') as f:
                f.write(client.files(gid, '{0}'.format(skymap_file)).read())
        paths_to_skymaps.append(path)

    return paths_to_redshifts, paths_to_skymaps
