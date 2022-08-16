from math import log10, log, exp

from numpy import linspace, exp as np_exp
from scipy.interpolate import BSpline, splrep

PARSEC_CM = 3.08567758128e18
RSUN_CM = 6.957e10

def convert_units(wave, flux, wave_units, flux_units):
    '''Convert from Phoenix wavelength and flux units to specified units.

    Phoenix wavelength and flux units are Å and erg/s/cm^2/cm.
    '''
    if flux_units == 'erg/s/cm2/cm':
        pass
    elif flux_units == 'Jy':
        flux *= 3.335641e-4 * wave**2
    elif flux_units == 'mJy':
        flux *= 3.335641e-4 * wave**2 * 1e3
    elif flux_units == 'ABmag':
        flux = -2.5 * log10(3.335641e-4 * wave**2 * flux / 3631)
    elif flux_units == 'photon/s/cm2/Å':
        flux *= 0.50341125 * wave
    elif flux_units == 'erg/s/cm2/Å':
        flux /= 1e8
    elif flux_units == 'Watt/m2/µm':
        flux /= 1e7
    else:
        raise ValueError(f'{flux_units} is not a known flux unit')

    if wave_units == 'Å':
        pass
    elif wave_units == 'µm':
        wave /= 1e4
    else:
        raise ValueError(f'{wave_units} is not a known wavelength unit')

    return wave, flux

def flux_at_earth(surface_flux, rstar_rsun, parallax_mas):
    '''Return flux at Earth, given surface flux, radius, and distance.'''
    rstar_cm = RSUN_CM * rstar_rsun
    distance_cm = PARSEC_CM * 1e3 / parallax_mas
    return surface_flux * (rstar_cm / distance_cm)**2

def make_binedges(wmin, wmax, resol, oversamp=2):
    '''Make wavelength bins with specified oversampling, given resolution.

    0.5 * (w1 + w0) / (w1 - w0) = R = resol * osamp
    2 * R = (w1 + w0) / (w1 - w0)
    2 * R * w1 - 2 * R * w0 = w1 + w0
    (2 * R - 1) * w1 = (2 * R + 1) * w0
    X = wratio = w1 / w0 = (2 * R + 1) / (2 * R - 1)

    w1 / w0 = X = wratio
    wn / w0 = X**n
    log(wn / w0) = n * log(X)
    nwave = log(wn / w0) / log(X)
    '''
    wratio = (2 * resol * oversamp + 1) / (2 * resol * oversamp - 1)
    nwave = round(log(wmax /wmin) / log(wratio))
    return np_exp(linspace(log(wmin), log(wmax), num=nwave))

def rebin_spectrum(wave, flux, binedges):
    '''Fit spectrum with B spline. Integrate B spline into new bins.'''

    spline_param = splrep(wave, flux)
    bspline = BSpline(*spline_param, extrapolate=True)
    binwave = [0.5 * (lo + hi) for lo, hi in zip(
        binedges[:-1], binedges[1:])]
    binflux = [bspline.integrate(lo, hi) / (hi - lo) for lo, hi in zip(
        binedges[:-1], binedges[1:])]
    return binwave, binflux
