# address
Allow you to operate address system

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.address',]
```

# chat
Allow you to operate chat system.
- support chatbox available
- internal chat between user
- and room chat

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.chat',]
```

# logger
Enhance the logging system with changes log model and events log model.

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.logger',]
```

# nationality
Allow you to operate a nationality system with number phone, country code and images flag.

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.nationality',]
```

# tenant
Allow you to operate a tenant system configurable.

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.tenant',]
```

# twofactor
Add a twofactor system by backend customizable.
- Email support
- SMS partially support
- Webapp (in progress)

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.twofactor',]
```

# user
Enhance the user system django.
- Multiple email and phone
- session with anonymous code for retrieve and support a future user.
- Save UserAgents and IPs.

settings.py:
```python
INSTALLED_APPS += ['mighty.applications.user',]
```