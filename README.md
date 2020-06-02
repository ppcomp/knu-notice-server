# knu-notice-server

```
Python
Django
VisualStudioCode
```

## Deploy settings
1. Create `secret.json` file to `knu_notice/config`.

2. Change `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')` to `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')` from
```
knu-notice/manage.py
knu-notice/settings/wsgi.py
```

3. Change `localhost` to `server ip addr` from
```
config/nginx/nginx.conf
```