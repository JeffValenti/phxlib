from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

class HiresFigure:
    '''Manage a figure plotting Phoenix HiRes spectra.'''

    def __init__(self, xmin, xmax, xunit, yunit, xlog=True, **kwargs):
        self.figure = Figure(layout='constrained')
        self.axes = self.figure.add_subplot(**kwargs)
        self.axes.set_xlim(xmin, xmax)
        self.axes.set_xlabel(f'Wavelength [{xunit}]')
        self.axes.set_ylabel(f'Flux at Earth [{yunit}]')
        if xlog:
            self.set_xlog()

    def set_xlog(self):
        self.axes.set_xscale('log')
        self.axes.xaxis.set_major_formatter(FuncFormatter(tick_formatter))

    def set_xticks(self, major=None, minor=None):
        if major:
            self.axes.xaxis.set_ticks(major)
        if minor:
            self.axes.xaxis.set_ticks(minor, minor=True)

    def plot(self, x, y, steplimit=20000, **kwargs):
        if len(x) < steplimit:
            self.axes.step(x, y, where='mid', **kwargs)
        else:
            self.axes.plot(x, y, **kwargs)

    def save(self, path):
        self.axes.legend(loc='upper right', fontsize='small')
        print(f'saving {path}')
        self.figure.savefig(path)

def tick_formatter(value, position):
    if value % 1 == 0:
        return f'{int(value)}'
    else:
        return f'{value:.1f}'
