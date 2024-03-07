from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from mighty.fields import RichTextField
from mighty.models.base import Base
from mighty.functions import make_searchable
from mighty.fields import JSONField
from mighty.filegenerator import FileGenerator
from mighty.functions import getattr_recursive
from mighty.translates import reporting as _
from functools import cached_property

class Reporting(Base):
    name = models.CharField(_.name, max_length=255)
    file_name = models.TextField(_.file_name, help_text=_.file_name_help, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True,
        related_name="ct_to_reporting", verbose_name=_.content_type, help_text=_.content_type_help)
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True,
        related_name="ct_to_target", verbose_name=_.target, help_text=_.target_help)
    manager = models.CharField(_.manager, max_length=255, default="objects", help_text=_.manager_help)
    config = JSONField(default=list, blank=True, null=True, help_text=_.config_help)
    filter_config = JSONField(_.filter_config, default=dict, blank=True, null=True, help_text=_.filter_config_help)
    filter_related = JSONField(_.filter_related, default=dict, blank=True, null=True, help_text=_.filter_related_help)
    is_detail = models.BooleanField(_.is_detail, default=False)
    can_excel = models.BooleanField(_.can_excel, default=True)
    cfg_excel = JSONField(_.cfg_excel, default=dict, blank=True, null=True)
    can_csv = models.BooleanField(_.can_csv, default=True)
    cfg_csv = JSONField(_.cfg_csv, default=dict, blank=True, null=True)
    can_pdf = models.BooleanField(_.can_pdf, default=False)
    cfg_pdf = JSONField(_.cfg_pdf, default=dict, blank=True, null=True)
    html_pdf = RichTextField(_.html_pdf, blank=True, null=True)
    email_html = RichTextField(_.email_html, blank=True, null=True)
    related_obj = None

    class Meta(Base.Meta):
        abstract = True
        ordering = ('name', 'content_type', 'target')
        verbose_name = _.verbose_name
        verbose_name_plural = _.verbose_name_plural

    def __str__(self):
        return self.name
    
    @property
    def reporting_export_name(self):
        return "%s_%s" % (self.file_name or self.name, timezone.now().strftime("%Y%m%d-%Hh%Ms%S"))
    
    @property
    def max_fields(self):
        return [mf for mf in self.config if mf.get("multiple")]
    
    @cached_property
    def reporting_max_aggregate(self):
        count_data = {"count_"+mf["data"]: models.Count(mf["data"]) for mf in self.max_fields}
        max_data = {mf["data"]: models.Max("count_"+mf["data"]) for mf in self.max_fields}
        qs = getattr_recursive(self.target.model_class(), self.manager).filter(**self.reporting_filter)
        return qs.annotate(**count_data).aggregate(**max_data)

    @property
    def reporting_filter(self):
        Qfilter = {}
        if self.filter_config:
            Qfilter.update(self.filter_config)
        if self.filter_related:
            Qfilter.update({k: self.reporting_data_obj(v, self.related_obj)
                for k,v in self.filter_related.items()})
        return Qfilter

    @property
    def reporting_queryset(self):
        return getattr_recursive(self.target.model_class(), self.manager).filter(**self.reporting_filter)

    @property
    def reporting_fields(self):
        data = []
        for cfg in self.config:
            head = cfg.get("label") or cfg.get("multiple") or cfg.get("data")
            if cfg.get("multiple"):
                max = self.reporting_max_aggregate.get(cfg["data"])
                if cfg.get("fields"):
                    data += [field+str(i+1) for i in range(0, max) for field in cfg["fields"]]
                else:
                    data += [head+str(i+1) for i in range(0, max)]
            elif cfg.get("fields"):
                data += [field for field in cfg["fields"]]
        return data

    def reporting_data_obj(self, field, obj, multiple=None):
        attr = getattr_recursive(obj, field)
        if multiple:
            return attr.all()
        return attr(obj) if callable(attr) else attr

    def reporting_get_data_multiple(self, cfg, obj):
        max = self.reporting_max_aggregate.get(cfg["data"])
        mlt = self.reporting_data_obj(cfg.get("data"), obj, cfg["multiple"])
        blk = max - len(mlt)
        if cfg.get("fields"):
            data = [getattr(d, field) for d in mlt for field in cfg["fields"]]
            data += ["" for i in range(len(mlt), blk) for field in cfg["fields"]]
        else:
            data = [getattr(d, cfg["multiple"]) for d in mlt]
            data += ["" for i in range(len(mlt), blk)]
        return data
    
    def reporting_get_data_fields(self, cfg, obj):
        return [self.reporting_data_obj(field, obj) for field in cfg["fields"]]
    
    def reporting_line_detail(self, obj):
        data = []
        for cfg in self.config:
            if cfg.get("multiple"):
                data += self.reporting_get_data_multiple(cfg, obj)
            elif cfg.get("fields"):
                data += self.reporting_get_data_fields(cfg, obj)
            else:
                data += [self.reporting_data_obj(cfg.get("data"), obj),]
        return data

    @property
    def reporting_items(self):
        return [self.reporting_line_detail(obj) for obj in self.reporting_queryset]

    @property
    def reporting_file_generator(self):
        return FileGenerator(
            filename=self.reporting_export_name,
            items=self.reporting_items,
            fields=self.reporting_fields
        )

    def reporting_file_response(self, response, file_type, *args, **kwargs):
        obj = kwargs.get('obj', None)
        if response == "http":
            return self.reporting_file_generator.response_http(file_type)
        elif response == "email":
            from mighty.models import Missive
            from django.template import Template, Context
            file = self.reporting_file_generator.file_csv(file_type, None)
            missive = Missive (
                target = self.email_target,
                subject = "Récapitulatif",
                html = Template(self.email_html).render(Context({'obj': self})),
                content_type=obj.get_content_type() if obj else None,
                object_id=obj.id if obj else None,
            )
            missive.attachments = [file]
            missive.save()

            return file

        return self.reporting_file_generator.response_file(file_type)
