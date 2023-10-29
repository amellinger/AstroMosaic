#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 19:33:22 2023

@author: axel
"""

from astropy.io import fits
# from astropy.coordinates import SkyCoord
from reproject.mosaicking import find_optimal_celestial_wcs, reproject_and_coadd
from reproject import reproject_interp
from astropy.wcs import WCS
import matplotlib.pyplot as plt

# Replace the file names with your own.
fnames = ['Sh2-157_F1_PixelMath_astrometry.fits', 'Sh2-157_F2_PixelMath_astrometry.fits']

# Weight files should have pixel values between 0 and 1. They must have the same dimensions as the images.
weights = ['Sh2-157_F1_PixelMath_astrometry.weight.fits', 'Sh2-157_F2_PixelMath_astrometry.weight.fits']

hdus_3D = [fits.open(fn)[0] for fn in fnames]


for color in range(3):
    # find_optimal_celestial_wcs only works on 2D images
    # Therefore we must slice the color fits cube.
    hdus_2D = []
    for hdu_3D in hdus_3D:
        w =  WCS(hdu_3D.header, naxis=2)
        hdu_2D = w.to_fits()[0]
        hdu_2D.data = hdu_3D.data[color,:,:]
        hdus_2D.append(hdu_2D)
    
    wcs_out, shape_out = find_optimal_celestial_wcs(hdus_2D)
    array, footprint = reproject_and_coadd(hdus_2D, wcs_out, shape_out=shape_out,
                                           reproject_function=reproject_interp,
                                           input_weights = weights,
                                           match_background=True)

    hdul_mosaic = wcs_out.to_fits()
    hdul_mosaic[0].data = array
    hdul_mosaic.writeto(f'mosaic_{color:01d}.fits', overwrite=True)
