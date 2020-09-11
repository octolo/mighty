from mighty.applications.grapher.backends    import GraphBackend


class RGraph(GraphBackend):

    @property
    def css(self):
        return {
            'canvas': 'rgraph/canvas/canvas.css',
            'svg': 'rgraph/svg/svg.css',
        }

    @property
    def html(self):
        return {
            'canvas': 'rgraph/canvas/canvas.html',
            'svg': 'rgraph/svg/svg.html',
        }

    @property
    def directory(self):
        return {
            'canvas': 'rgraph/canvas/',
            'svg': 'rgraph/svg/',
        }

    @property
    def common_lib(self):
        return {
            'canvas': 'js/RGraph/libraries/RGraph.common.core.js',
            'svg': 'js/RGraph/libraries/RGraph.svg.common.core.js',
        }

    @property
    def ajax_lib(self):
        return {
            'canvas': 'js/RGraph/libraries/RGraph.common.ajax.js',
            'svg': 'js/RGraph/libraries/RGraph.svg.common.ajax.js',
        }

    @property
    def svg_lib(self):
        return {
            self.bar: 'js/RGraph/libraries/RGraph.svg.bar.js',
            self.bipolar: 'js/RGraph/libraries/RGraph.svg.bipolar.js',
            self.funnel: 'js/RGraph/libraries/RGraph.svg.funnel.js',
            self.gauge: 'js/RGraph/libraries/RGraph.svg.gauge.js',
            self.horizontalbar: 'js/RGraph/libraries/RGraph.svg.hbar.js',
            self.horizontalprogressbars: 'js/RGraph/libraries/RGraph.svg.horizontalprogressbars.js',
            self.line: 'js/RGraph/libraries/RGraph.svg.line.js',
            self.pie: 'js/RGraph/libraries/RGraph.svg.pie.js',
            self.radar: 'js/RGraph/libraries/RGraph.svg.radar.js',
            self.rose: 'js/RGraph/libraries/RGraph.svg.rose.js',
            self.scatter: 'js/RGraph/libraries/RGraph.svg.scatter.js',
            self.semicircularprogressbars: 'js/RGraph/libraries/RGraph.svg.semicircularprogressbars.js',
            self.verticalprogressbars: 'js/RGraph/libraries/RGraph.svg.verticalprogressbars.js',
            self.waterfall: 'js/RGraph/libraries/RGraph.svg.waterfall.js',
            self.donut: 'js/RGraph/libraries/RGraph.svg.donut.js',
            self.gantt: 'js/RGraph/libraries/RGraph.svg.gantt.js',
            self.meter: 'js/RGraph/libraries/RGraph.svg.meter.js',
            self.odometer: 'js/RGraph/libraries/RGraph.svg.odometer.js',
            self.radialscatter: 'js/RGraph/libraries/RGraph.svg.radialscatter.js',
            self.thermometer: 'js/RGraph/libraries/RGraph.svg.thermometer.js',
        }

    @property
    def canvas_lib(self):
        return {
            self.bar: 'js/RGraph/libraries/RGraph.bar.js',
            self.bipolar: 'js/RGraph/libraries/RGraph.bipolar.js',
            self.funnel: 'js/RGraph/libraries/RGraph.funnel.js',
            self.gauge: 'js/RGraph/libraries/RGraph.gauge.js',
            self.horizontalbar: 'js/RGraph/libraries/RGraph.hbar.js',
            self.horizontalprogressbars: 'js/RGraph/libraries/RGraph.horizontalprogressbars.js',
            self.line: 'js/RGraph/libraries/RGraph.line.js',
            self.pie: 'js/RGraph/libraries/RGraph.pie.js',
            self.radar: 'js/RGraph/libraries/RGraph.radar.js',
            self.rose: 'js/RGraph/libraries/RGraph.rose.js',
            self.scatter: 'js/RGraph/libraries/RGraph.scatter.js',
            self.semicircularprogressbars: 'js/RGraph/libraries/RGraph.semicircularprogressba.js',
            self.verticalprogressbars: 'js/RGraph/libraries/RGraph.verticalprogressbars.js',
            self.waterfall: 'js/RGraph/libraries/RGraph.waterfall.js',
            self.donut: 'js/RGraph/libraries/RGraph.donut.js',
            self.gantt: 'js/RGraph/libraries/RGraph.gantt.js',
            self.meter: 'js/RGraph/libraries/RGraph.meter.js',
            self.odometer: 'js/RGraph/libraries/RGraph.odometer.js',
            self.radialscatter: 'js/RGraph/libraries/RGraph.radialscatter.js',
            self.thermometer: 'js/RGraph/libraries/RGraph.thermometer.js',
        }