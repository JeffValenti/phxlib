from matplotlib.figure import Figure


class HiresFigure:
    '''Manage a figure plotting Phoenix HiRes spectra.'''

    def __init__(self):
        self.figure = Figure()
        self.axes = self.figure.add_subplot()

    def plot(self, x, y, **kwargs):
        self.axes.plot(x, y, **kwargs)

    def save(self, path):
        print(f'saving {path}')
        self.figure.savefig(path)
