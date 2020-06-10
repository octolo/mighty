# Tenant
The tenant application allows you to conceptualize the application around a tenant.
All you need is to configure two properties.

## Configuration
You are able to configure two foreignkeys, **tenant ** and **user**.

- **tenant** default is **auth.Group**
- **user** default is **mighty.User**

You can override this configuration from the settings.py like this:

    TENANT = {'ForeignKey': {'tenant': 'app_label.Model', 'user': 'app_label.Model'}}

## Usage
At this point you can operate your application with her new tenant capability.

- **tenant** related_name is **tenant_tenant**
- **user** related_name is **user_tenant**