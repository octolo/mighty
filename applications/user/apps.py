from django.apps import AppConfig
from django.conf import settings

#from mighty import stdtypes

class Config:
    class Field:
        username = 'email'
        required = ()

#def over_config(conf, var)
#    if hasattr(settings, var):
#        for key, val in getattr(settings, var).items():
#            if hasattr(conf, key):
#                if type(val) in stdtypes['mapping'] and type(getattr(conf, key)) not in stdtypes['mapping']:
#                    for key2,val2 in val.items():
#                        if hasattr(getattr(conf, key), key):
#                            setattr(getattr(conf, key), key2, val2)
#                else:
#                    setattr(conf, key, val)
#            else:
#                setattr(conf, key, val)
#
#over_config(Config, 'USER')



if hasattr(settings, 'USER'):
    for config,configs in getattr(settings, 'USER').items():
        if hasattr(Config, config):
            for key,value in configs.items():
                if hasattr(getattr(Config, config), key):
                    setattr(getattr(Config, config), key, value)

class UserConfig(AppConfig, Config):
    name = 'mighty.applications.user'

    def ready(self):
        from . import signals