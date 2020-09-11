from mighty.admin.models import BaseAdmin
from mighty.applications.grapher import fields, translates as _

class TemplateAdmin(BaseAdmin):
    view_on_site = False
    fieldsets = (((None, {'fields': fields.template})),
        ("Options", {'classes': ('collapse',), 'fields': fields.template_options}),
        ("Large", {'classes': ('collapse',), 'fields': fields.template_lg}),
        ("Medium", {'classes': ('collapse',), 'fields': fields.template_md}),
        ("Small", {'classes': ('collapse',), 'fields': fields.template_sm}),)
    list_display = ('name',)

class GraphicAdmin(BaseAdmin):
    fieldsets = (((None, {'fields': fields.graphic})),
        ("Options", {'classes': ('collapse',), 'fields': fields.graphic_options}),
        ("Size", {'classes': ('collapse',), 'fields': fields.graphic_size}),
        (_.BAR, {'classes': ('collapse',), 'fields': ('bar_values',) }),
        (_.BIPOLAR, {'classes': ('collapse',), 'fields': ('bipolar_values',) }),
        (_.FUNNEL, {'classes': ('collapse',), 'fields': ('funnel_values',) }),
        (_.GAUGE, {'classes': ('collapse',), 'fields': ('gauge_values',) }),
        (_.HORIZONTALBAR, {'classes': ('collapse',), 'fields': ('horizontalbar_values',) }),
        (_.HORIZONTALPROGRESSBARS, {'classes': ('collapse',), 'fields': ('horizontalprogressbars_values',) }),
        (_.LINE, {'classes': ('collapse',), 'fields': ('line_values',) }),
        (_.PIE, {'classes': ('collapse',), 'fields': ('pie_values',) }),
        (_.RADAR, {'classes': ('collapse',), 'fields': ('radar_values',) }),
        (_.ROSE, {'classes': ('collapse',), 'fields': ('rose_values',) }),
        (_.SCATTER, {'classes': ('collapse',), 'fields': ('scatter_values',) }),
        (_.SEMICIRCULARPROGRESSBARS, {'classes': ('collapse',), 'fields': ('semicircularprogressbars_values',) }),
        (_.VERTICALPROGRESSBARS, {'classes': ('collapse',), 'fields': ('verticalprogressbars_values',) }),
        (_.WATERFALL, {'classes': ('collapse',), 'fields': ('waterfall_values',) }),
        (_.DONUT, {'classes': ('collapse',), 'fields': ('donut_values',) }),
        (_.GANTT, {'classes': ('collapse',), 'fields': ('gantt_values',) }),
        (_.METER, {'classes': ('collapse',), 'fields': ('meter_values',) }),
        (_.ODOMETER, {'classes': ('collapse',), 'fields': ('odometer_values',) }),
        (_.RADIALSCATTER, {'classes': ('collapse',), 'fields': ('radialscatter_values',) }),
        (_.THERMOMETER, {'classes': ('collapse',), 'fields': ('thermometer_values',) }),
    )
    list_display = ('title', 'svg_url_html', 'canvas_url_html')
    filter_horizontal = ('templates',)