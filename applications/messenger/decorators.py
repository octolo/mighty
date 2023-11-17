from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from mighty.applications.user.apps import UserConfig as user_conf
from mighty.applications.messenger import choices
from mighty.applications.messenger import notify, notify_discord, notify_slack
import hashlib

def MissiveFollower(**kwargs):
    def decorator(obj):
        class MFModel(obj):
            priority = models.PositiveIntegerField(default=0, choices=choices.PRIORITIES)
            missive = models.ForeignKey(user_conf.ForeignKey.missive,
                on_delete=kwargs.get('on_delete', models.SET_NULL),
                related_name=kwargs.get('related_name', 'missive_set'),
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
            )
            missives = GenericRelation(user_conf.ForeignKey.missive)

            class Meta(obj.Meta):
                abstract = True

        return MFModel
    return decorator

def NotifyByCondition(**kwargs):
    def decorator(obj):
        class NBCModel(obj):
            nbc_fields_compare = ("subject", "html", "txt", "mode", "target")
            nbc_startswith = "nbc_"
            nbc_prefix = "trigger_"
            nbc_notify = "notify_"
            nbc_notify_status = True
            nbc_notify_active = models.BooleanField(default=True)
            nbc_last_notify = models.ForeignKey("mighty.Missive", on_delete=models.SET_NULL, blank=True, null=True)

            class Meta(obj.Meta):
                abstract = True

            @property
            def nbc_last_notify_hash(self):
                if self.nbc_last_notify is not None:
                    last_md5 = "".join([getattr(self.nbc_last_notify, field, "") for field in self.nbc_fields_compare])
                    return hashlib.md5(last_md5).hexdigest()
                return None

            def nbc_notify_if_different(self, **kwargs):
                last_md5 = self.nbc_last_notify_hash
                new_md5 = "".join([str(getattr(kwargs, field, "")) for field in self.nbc_fields_compare])
                new_md5 = hashlib.md5(new_md5).hexdigest()
                if last_md5 != new_md5:
                    return self.nbc_do_notify(**kwargs)

            def nbc_do_notify(self, **kwargs):
                ct, pk = self.get_content_type(), self.id
                return notify(kwargs.pop("subject"), ct, pk, **kwargs)

            def nbc_get_template(self, name, subject=None):
                from mighty.models import Template as TPL
                from django.template import Context, Template
                try:
                    tpl = TPL.objects.get(name=name)
                    sbj = tpl.subject
                    tpl = Template(self.nbc_wrapper_or_none(tpl.template)).render(Context(self.nbc_context_or_none))
                except TPL.DoesNotExist:
                    from django.template.loader import get_template
                    sbj = subject
                    tpl = get_template(self.nbc_dir_notifications_or_none+name+".html").template.source
                    tpl_tosave = TPL(name=name, subject=subject, template=tpl)
                    tpl_tosave.save()
                    tpl = Template(self.nbc_wrapper_or_none(tpl)).render(Context(self.nbc_context_or_none))
                sbj = Template(self.nbc_wrapper_or_none(sbj)).render(Context(self.nbc_context_or_none))
                return tpl, sbj

            def disable_nbc_notify(self):
                self.nbc_notify_active = False

            def enable_nbc_notify(self):
                self.nbc_notify_status = self.nbc_notify_active
                self.nbc_notify_active = True

            @property
            def nbc_dir_notifications_or_none(self):
                return self.nbc_dir_notifications if hasattr(self, "nbc_dir_notifications") else "notifications/"

            @property
            def nbc_context_or_none(self):
                return self.nbc_context if hasattr(self, "nbc_context") else {}

            def nbc_wrapper_or_none(self, tpl):
                if hasattr(self, "nbc_wrapper"):
                    wrp = self.nbc_wrapper.split("{{ content }}")
                    return wrp[0]+tpl+wrp[1]
                return tpl

            @property
            def nbc_list(self):
                return [p for p in dir(self) if p.startswith(self.nbc_startswith)]

            @property
            def nbc_list_trigger(self):
                return [p for p in self.nbc_list
                    if p.startswith(self.nbc_startswith + self.nbc_prefix)]

            def nbc_trigger(self):
                pass
                #if self.nbc_notify_status:
                #    for nbc in self.nbc_list_trigger:
                #        nbc_notify = self.nbc_startswith + self.nbc_notify
                #        nbc_notify = nbc.replace(self.nbc_startswith + self.nbc_prefix, nbc_notify)
                #        if hasattr(self, nbc_notify) and getattr(self, nbc)():
                #            getattr(self, nbc_notify)()
        return NBCModel
    return decorator
