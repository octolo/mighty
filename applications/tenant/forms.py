from mighty.forms import ModelFormDescriptable
from mighty.applications.tenant import get_tenant_model

#TenantModel = get_tenant_model()
#TenantGroup = get_tenant_model(conf.ForeignKey.group)
TenantSetting = get_tenant_model(conf.ForeignKey.fksetting)
#RoleModel = get_tenant_model(conf.ForeignKey.role)

class SettingFullForm(ModelFormDescriptable):
    class Meta:
        model = TenantSetting
        fields = ('name', 'config_char', 'config_json', 'config_rich', 'config_text')

class SettingCharForm(ModelFormDescriptable):
    class Meta:
        model = TenantSetting
        fields = ('name', 'config_char')

class SettingJsonForm(ModelFormDescriptable):
    class Meta:
        model = TenantSetting
        fields = ('name', 'config_json')

class SettingRichForm(ModelFormDescriptable):
    class Meta:
        model = TenantSetting
        fields = ('name', 'config_rich')

class SettingTextForm(ModelFormDescriptable):
    class Meta:
        model = TenantSetting
        fields = ('name', 'config_text')