from mighty.applications.grapher import models

class GraphBackend:
    bar = models.BAR
    bipolar = models.BIPOLAR
    funnel = models.FUNNEL
    gauge = models.GAUGE
    horizontalbar = models.HORIZONTALBAR
    horizontalprogressbars = models.HORIZONTALPROGRESSBARS
    line = models.LINE
    pie = models.PIE
    radar = models.RADAR
    rose = models.ROSE
    scatter = models.SCATTER
    semicircularprogressbars = models.SEMICIRCULARPROGRESSBARS
    verticalprogressbars = models.VERTICALPROGRESSBARS
    waterfall = models.WATERFALL
    donut = models.DONUT
    gantt = models.GANTT
    meter = models.METER
    odometer = models.ODOMETER
    radialscatter = models.RADIALSCATTER
    thermometer = models.THERMOMETER

    def __init__(self, graphic): self.graphic = graphic
    @property
    def css(self): raise NotImplementedError('Property css not implemented in %s' % type(self).__name__)
    @property
    def html(self): raise NotImplementedError('Property html not implemented in %s' % type(self).__name__)
    @property
    def directory(self): raise NotImplementedError('Property directory not implemented in %s' % type(self).__name__)
    @property
    def common_lib(self): raise NotImplementedError('Property common_lib not implemented in %s' % type(self).__name__)
    @property
    def ajax_lib(self): raise NotImplementedError('Property ajax_lib not implemented in %s' % type(self).__name__)
    @property
    def svg_lib(self): raise NotImplementedError('Property svg_lib not implemented in %s' % type(self).__name__)
    @property
    def canvas_lib(self): raise NotImplementedError('Property canvas_lib not implemented in %s' % type(self).__name__)

    def libraries(self, gtype='svg'):
        config = getattr(self, '%s_lib' % gtype)
        libraries = [self.common_lib[gtype],]
        for template in self.graphic.templates.all():
            library = config[template.graphtype]
            if library not in libraries:
                libraries.append(library)
        return libraries