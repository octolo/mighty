from django.db import models
from django.utils.html import mark_safe
from django.template import Context, Template

from mighty.models import JSONField
from mighty.models.base import Base
from mighty.models.uid import Uid
from mighty.applications.grapher import translates as _

BAR = "BAR"
BIPOLAR = "BIPOLAR"
FUNNEL = "FUNNEL"
GAUGE = "GAUGE"
HORIZONTALBAR = "HORIZONTALBAR"
HORIZONTALPROGRESSBARS = "HORIZONTALPROGRESSBARS"
LINE = "LINE"
PIE = "PIE"
RADAR = "RADAR"
ROSE = "ROSE"
SCATTER = "SCATTER"
SEMICIRCULARPROGRESSBARS = "SEMICIRCULARPROGRESSBARS"
VERTICALPROGRESSBARS = "VERTICALPROGRESSBARS"
WATERFALL = "WATERFALL"
DONUT = "DONUT"
GANTT = "GANTT"
METER = "METER"
ODOMETER = "ODOMETER"
RADIALSCATTER = "RADIALSCATTER"
THERMOMETER = "THERMOMETER"
choices = (
    (BAR, _.BAR),
    (BIPOLAR, _.BIPOLAR),
    (FUNNEL, _.FUNNEL),
    (GAUGE, _.GAUGE),
    (HORIZONTALBAR, _.HORIZONTALBAR),
    (HORIZONTALPROGRESSBARS, _.HORIZONTALPROGRESSBARS),
    (LINE, _.LINE),
    (PIE, _.PIE),
    (RADAR, _.RADAR),
    (ROSE, _.ROSE),
    (SCATTER, _.SCATTER),
    (SEMICIRCULARPROGRESSBARS, _.SEMICIRCULARPROGRESSBARS),
    (VERTICALPROGRESSBARS, _.VERTICALPROGRESSBARS),
    (WATERFALL, _.WATERFALL),
    (DONUT, _.DONUT),
    (GANTT, _.GANTT),
    (METER, _.METER),
    (ODOMETER, _.ODOMETER),
    (RADIALSCATTER, _.RADIALSCATTER),
    (THERMOMETER, _.THERMOMETER),
)

class Template(Base):
    name = models.CharField(_.name, max_length=255, unique=True)
    graphtype = models.CharField(_.graphtype, choices=choices, max_length=100, default=BAR)

    lg_width = models.PositiveSmallIntegerField(_.lg_width, default=800)
    lg_height = models.PositiveSmallIntegerField(_.lg_height, default=400)
    lg_max_width = models.PositiveSmallIntegerField(_.lg_max_width, default=1200)
    lg_title_size = models.PositiveSmallIntegerField(_.lg_title_size, default=18)
    lg_text_size = models.PositiveSmallIntegerField(_.lg_text_size, default=14)
    lg_margin_inner = models.PositiveSmallIntegerField(_.lg_margin_inner, default=25)

    md_width = models.PositiveSmallIntegerField(_.md_width, default=600)
    md_height = models.PositiveSmallIntegerField(_.md_height, default=300)
    md_max_width = models.PositiveSmallIntegerField(_.md_max_width, default=992)
    md_title_size = models.PositiveSmallIntegerField(_.md_title_size, default=14)
    md_text_size = models.PositiveSmallIntegerField(_.md_text_size, default=12)
    md_margin_inner = models.PositiveSmallIntegerField(_.md_margin_inner, default=20)

    sm_width = models.PositiveSmallIntegerField(_.sm_width, default=400)
    sm_height = models.PositiveSmallIntegerField(_.sm_height, default=200)
    sm_max_width = models.PositiveSmallIntegerField(_.sm_max_width, default=768)
    sm_title_size = models.PositiveSmallIntegerField(_.sm_title_size, default=12)
    sm_text_size = models.PositiveSmallIntegerField(_.sm_text_size, default=10)
    sm_margin_inner = models.PositiveSmallIntegerField(_.sm_margin_inner, default=10)

    options = JSONField(blank=True, null=True)
    responsive_options = JSONField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_template
        verbose_name_plural = _.vp_template

    def __str__(self):
        return self.name

    def cleaner(self):
        import json
        if self.options:
            try:
                self.options = json.loads(self.options)
            except Exception:
                pass
        if self.responsive_options:
            try:
                self.responsive_options = json.loads(self.responsive_options)
            except Exception:
                pass

class Graphic(Uid, Base):
    title = models.CharField(_.title, max_length=255)
    is_responsive = models.BooleanField(_.is_responsive, default=False)

    svg_container = models.TextField(_.svg_container, blank=True, null=True)
    canvas_container = models.TextField(_.canvas_container, blank=True, null=True)

    width = models.PositiveSmallIntegerField(_.width, default=800)
    height = models.PositiveSmallIntegerField(_.height, default=400)
    max_width = models.PositiveSmallIntegerField(_.max_width, default=1200)
    title_size = models.PositiveSmallIntegerField(_.title_size, default=18)
    text_size = models.PositiveSmallIntegerField(_.text_size, default=14)
    margin_inner = models.PositiveSmallIntegerField(_.margin_inner, default=25)

    options = JSONField(blank=True, null=True)
    responsive_options = JSONField(blank=True, null=True)

    bar_values = JSONField(blank=True, null=True)
    bipolar_values = JSONField(blank=True, null=True)
    funnel_values = JSONField(blank=True, null=True)
    gauge_values = JSONField(blank=True, null=True)
    horizontalbar_values = JSONField(blank=True, null=True)
    horizontalprogressbars_values = JSONField(blank=True, null=True)
    line_values = JSONField(blank=True, null=True)
    pie_values = JSONField(blank=True, null=True)
    radar_values = JSONField(blank=True, null=True)
    rose_values = JSONField(blank=True, null=True)
    scatter_values = JSONField(blank=True, null=True)
    semicircularprogressbars_values = JSONField(blank=True, null=True)
    verticalprogressbars_values = JSONField(blank=True, null=True)
    waterfall_values = JSONField(blank=True, null=True)
    donut_values = JSONField(blank=True, null=True)
    gantt_values = JSONField(blank=True, null=True)
    meter_values = JSONField(blank=True, null=True)
    odometer_values = JSONField(blank=True, null=True)
    radialscatter_values = JSONField(blank=True, null=True)
    thermometer_values = JSONField(blank=True, null=True)

    class Meta(Base.Meta):
        abstract = True
        verbose_name = _.v_graph
        verbose_name_plural = _.vp_graph

    def __str__(self):
        return self.title

    @property
    def get_svg_container(self): return Template(self.svg_container).render(Context({'object': self,}))
    @property
    def get_canvas_container(self): return Template(self.canvas_container).render(Context({'object': self,}))
    @property
    def svg_url(self): return self.get_url('svg', arguments={"uid": self.uid})
    @property
    def svg_url_html(self): return self.get_url_html(self.get_url('svg', arguments={"uid": self.uid}), self.title)
    @property
    def canvas_url(self): return self.get_url('canvas', arguments={"uid": self.uid})
    @property
    def canvas_url_html(self): return self.get_url_html(self.get_url('canvas', arguments={"uid": self.uid}), self.title)

    def cleaner(self):
        import json
        if self.options:
            try:
                self.options = json.loads(self.options)
            except Exception:
                pass
        if self.responsive_options:
            try:
                self.responsive_options = json.loads(self.responsive_options)
            except Exception:
                pass
        if self.bar_values:
            try:
                self.bar_values = json.loads(self.bar_values)
            except Exception:
                pass
        if self.bipolar_values:
            try:
                self.bipolar_values = json.loads(self.bipolar_values)
            except Exception:
                pass
        if self.funnel_values:
            try:
                self.funnel_values = json.loads(self.funnel_values)
            except Exception:
                pass
        if self.gauge_values:
            try:
                self.gauge_values = json.loads(self.gauge_values)
            except Exception:
                pass
        if self.horizontalbar_values:
            try:
                self.horizontalbar_values = json.loads(self.horizontalbar_values)
            except Exception:
                pass
        if self.horizontalprogressbars_values:
            try:
                self.horizontalprogressbars_values = json.loads(self.horizontalprogressbars_values)
            except Exception:
                pass
        if self.line_values:
            try:
                self.line_values = json.loads(self.line_values)
            except Exception:
                pass
        if self.pie_values:
            try:
                self.pie_values = json.loads(self.pie_values)
            except Exception:
                pass
        if self.radar_values:
            try:
                self.radar_values = json.loads(self.radar_values)
            except Exception:
                pass
        if self.rose_values:
            try:
                self.rose_values = json.loads(self.rose_values)
            except Exception:
                pass
        if self.scatter_values:
            try:
                self.scatter_values = json.loads(self.scatter_values)
            except Exception:
                pass
        if self.semicircularprogressbars_values:
            try:
                self.semicircularprogressbars_values = json.loads(self.semicircularprogressbars_values)
            except Exception:
                pass
        if self.verticalprogressbars_values:
            try:
                self.verticalprogressbars_values = json.loads(self.verticalprogressbars_values)
            except Exception:
                pass
        if self.waterfall_values:
            try:
                self.waterfall_values = json.loads(self.waterfall_values)
            except Exception:
                pass
        if self.donut_values:
            try:
                self.donut_values = json.loads(self.donut_values)
            except Exception:
                pass
        if self.gantt_values:
            try:
                self.gantt_values = json.loads(self.gantt_values)
            except Exception:
                pass
        if self.meter_values:
            try:
                self.meter_values = json.loads(self.meter_values)
            except Exception:
                pass
        if self.odometer_values:
            try:
                self.odometer_values = json.loads(self.odometer_values)
            except Exception:
                pass
        if self.radialscatter_values:
            try:
                self.radialscatter_values = json.loads(self.radialscatter_values)
            except Exception:
                pass
        if self.thermometer_values:
            try:
                self.thermometer_values = json.loads(self.thermometer_values)
            except Exception:
                pass