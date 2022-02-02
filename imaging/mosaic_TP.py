import reproject
from astropy import units as u
from astropy.io import fits
from astropy import coordinates
from astropy import wcs
from spectral_cube import SpectralCube
from reproject import reproject_interp
from reproject.mosaicking import find_optimal_celestial_wcs, reproject_and_coadd

basepath = '/orange/adamginsburg/ACES/'

# target_wcs = wcs.WCS(naxis=2)
# target_wcs.wcs.ctype = ['GLON-CAR', 'GLAT-CAR']
# target_wcs.wcs.crval = [0, 0]
# target_wcs.wcs.cunit = ['deg', 'deg']
# target_wcs.wcs.cdelt = [-6.38888888888888e-4, 6.388888888888888e-4]
# target_wcs.wcs.crpix = [2000, 2000]
# 
# header = target_wcs.to_header()
# header['NAXIS1'] = 4000
# header['NAXIS2'] = 4000

import glob

filelist = glob.glob(f'{basepath}/rawdata/2021.1.00172.L/s*/g*/m*/product/*spw17.cube.I.sd.fits')

def read_as_2d(fn):
    cube = SpectralCube.read(fn)
    mx = cube.max(axis=0)
    return mx.hdu

hdus = [read_as_2d(fn) for fn in filelist]

target_wcs, shape_out = find_optimal_celestial_wcs(hdus, frame='galactic')

array, footprint = reproject_and_coadd(hdus,
                                       target_wcs, shape_out=shape_out,
                                       reproject_function=reproject_interp)

fits.PrimaryHDU(data=array, header=target_wcs.to_header()).writeto(f'{basepath}/mosaics/TP_spw17mx_mosaic.fits', overwrite=True)

import pylab as pl
from astropy import visualization
pl.rc('axes', axisbelow=True)
pl.matplotlib.use('agg')

front = 10
back = -10

fig = pl.figure(figsize=(20,7))
ax = fig.add_subplot(111, projection=target_wcs)
im = ax.imshow(array, norm=visualization.simple_norm(array, stretch='asinh'), zorder=front)
pl.colorbar(mappable=im)
ax.coords[0].set_axislabel('Galactic Longitude')
ax.coords[1].set_axislabel('Galactic Latitude')
ax.coords[0].set_major_formatter('d.dd')
ax.coords[1].set_major_formatter('d.dd')
ax.coords[0].set_ticks(spacing=0.1*u.deg)
ax.coords[0].set_ticklabel(rotation=45, pad=20)


fig.savefig(f'{basepath}/mosaics/TP_spw17mx_mosaic.png', bbox_inches='tight')

ax.coords.grid(True, color='black', ls='--', zorder=back)

overlay = ax.get_coords_overlay('icrs')
overlay.grid(color='black', ls=':', zorder=back)
overlay[0].set_axislabel('Right Ascension (ICRS)')
overlay[1].set_axislabel('Declination (ICRS)')
overlay[0].set_major_formatter('hh:mm')
ax.set_axisbelow(True)
ax.set_zorder(back)
fig.savefig(f'{basepath}/mosaics/TP_spw17mx_mosaic_withgrid.png', bbox_inches='tight')
