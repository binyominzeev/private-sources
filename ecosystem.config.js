module.exports = {
  apps: [{
    name: 'private-sources',
    script: 'gunicorn',
    args: 'private_sources.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 120',
    cwd: '/var/www/private-sources',
    interpreter: '/var/www/private-sources/venv/bin/python',
    env: {
      'DJANGO_SECRET_KEY': 'your-secret-key-here',
      'DJANGO_DEBUG': 'False',
      'DJANGO_ALLOWED_HOSTS': 'translations.myshiurim.com',
      'PATH': '/var/www/private-sources/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '500M',
    autorestart: true,
    error_file: '/var/www/private-sources/logs/pm2-error.log',
    out_file: '/var/www/private-sources/logs/pm2-out.log',
  }]
};
