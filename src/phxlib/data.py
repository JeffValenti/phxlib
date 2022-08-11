from bisect import bisect_right
from os import getenv
from pathlib import Path

from astropy.io.fits import open as fits_open

class PhoenixData:
    '''Manage access to Phoenix data on disk. '''

    def __init__(self, root=None, version='v1.0'):
        self.set_root(root=root)
        self.version = version
        self.eos = 'PHOENIX-ACES-AGSS-COND-2011'
        self.teff_grid = [
            *range(2300, 6901, 100),
            *range(7000, 12001, 200),
            *range(12500, 15001, 500)]
        self.logg_grid = [-0.5, 0, 0.5, 1, 0.1, 2, 2.5,
            3, 3.5, 4, 4.5, 5, 5.5, 6]
        self.fe_grid = [-4, -3, -2, -1.5, -1, -0.5, 0, 0.5, 1]

    def set_root(self, root=None):
        '''Set path to top level directory containing Phoenix data.'''
        if root:
            self.root = root
        else:
            try:
                self.root = Path(getenv('PHXDATA'))
            except TypeError as e:
                e.args = ('PHXDATA environment variable is not set', *e.args)
                raise

    def bracket_value(self, grid, value, param='value'):
        '''Get grid values that bracket specfied value.'''
        if value in grid:
            return [value]
        else:
            igrid = bisect_right(grid, value)
            if igrid == 0 or igrid == len(grid):
                raise ValueError(f'{param}={value} is outside grid')
            return [grid[igrid - 1], grid[igrid]]

    def get_subgrid(self, teff, logg, fe):
        '''Get grid values that bracket specfied stellar parameters.'''
        teff_bracket = self.bracket_value(self.teff_grid, teff, 'teff')
        logg_bracket = self.bracket_value(self.logg_grid, logg, 'logg')
        fe_bracket = self.bracket_value(self.fe_grid, fe, 'fe')
        return {'teff': teff_bracket, 'logg': logg_bracket, 'fe': fe_bracket}

    def get_path(self, filetype, teff, logg, fe):
        '''Generate path to requested data product.'''
        teff_str = f'{int(teff):05}'
        if logg == 0:
            logg_str = '-0.00'
        else:
            logg_str = f'{float(-logg):+0.2f}'
        if fe == 0:
            fe_str = f'-0.0'
        else:
            fe_str = f'{float(fe):+0.1f}'
        if filetype == 'hires':
            name = f'lte{teff_str}{logg_str}{fe_str}.{self.eos}-HiRes.fits'
            path = self.root / self.version / 'HiResFITS' \
                / self.eos / f'Z{fe_str}' / name
            return path
        else:
            raise RuntimeError(f'unknown filetype: {filetype}')

    def read_hires_wave(self):
        '''Read wavelength scale for high-resolution flux spectra.'''
        path = self.root / self.version / 'HiResFITS' / f'WAVE_{self.eos}.fits'
        with fits_open(path) as hdulist:
            wave = hdulist[0].data
        return wave

    def read_hires_flux(self, teff, logg, fe):
        '''Read high-resolution flux spectrum.'''
        path = self.get_path('hires', teff, logg, fe)
        with fits_open(path) as hdulist:
            flux = hdulist[0].data
        return flux

    def interpolate_hires_flux(self, teff, logg, fe):
        '''Interpolate in grid of high-resolution flux spectra.'''
        subgrid = get_subgrid(teff, logg, fe)
