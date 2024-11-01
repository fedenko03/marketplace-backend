# marketplace-backend

# Django Marketplace Project Setup

This guide provides instructions on setting up a Django project configured with MongoDB, Gunicorn, Nginx, Supervisor, and additional functionality for a marketplace application.

## Project Setup

### Prerequisites

1. **Ubuntu** server.
2. **Python 3.9** installed.
3. **MongoDB** for the database.
4. **Supervisor** for managing processes.
5. **Gunicorn** as the WSGI HTTP server.
6. **Nginx** as the reverse proxy server.
7. **Git** to pull the project from the repository.

### 1. Install Python 3.9

Install Python 3.9 if not already installed:
```bash
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev
```

### 2. Set Up the Virtual Environment and Dependencies
1 - Create a project directory and set up a virtual environment:

```bash
mkdir /home/ubuntu/backend
cd /home/ubuntu/backend
python3.9 -m venv venv
source venv/bin/activate
```

2 - Install the dependencies from requirements.txt:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Django Settings

Edit `settings.py` with the following changes:

#### Update `ALLOWED_HOSTS`

```python
ALLOWED_HOSTS = ['*']
```

#### Set the `BASE_URL` for your server

```python
BASE_URL = 'http://<your-server-ip>'
```

#### Configure Static and Media File Handling

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### Add MongoDB Database Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'FinalDB',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb://localhost:27017',
            'username': '<your-username>',
            'password': '<your-password>',
        }
    }
}
```

### 4. MongoDB Setup

Install and configure MongoDB:

```bash
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org
```

Start and enable MongoDB:

```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 5. Collect Static Files

Run Django’s collectstatic command:

```bash
python manage.py collectstatic --noinput
```

### 6. Set Up Gunicorn with Supervisor

Create a Supervisor configuration file for Gunicorn:

#### `/etc/supervisor/conf.d/gunicorn.conf`

```ini
[program:gunicorn]
directory=/home/ubuntu/backend
command=/home/ubuntu/backend/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/backend/gunicorn.sock backend.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/gunicorn.err.log
stdout_logfile=/var/log/gunicorn/gunicorn.out.log
user=ubuntu
umask=007

[group:guni]
programs=gunicorn
```

Activate the Supervisor configuration:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gunicorn
```

### 7. Configure Nginx

Create an Nginx configuration file for the Django project:

#### `/etc/nginx/sites-available/backend`

```nginx
server {
    listen 80;
    server_name <your-server-ip>;

    location /api/ {
        proxy_pass http://unix:/home/ubuntu/backend/gunicorn.sock;
        proxy_read_timeout 600s;
        include proxy_params;
    }

    location /static/ {
        alias /home/ubuntu/backend/static/;
    }

    location /media/ {
        alias /home/ubuntu/backend/media/;
    }
}
```

Activate the Nginx configuration and restart:

```bash
sudo ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Initialize Django Application

- Apply migrations:

```bash
  python manage.py migrate
```

- Create a superuser for the Django admin panel:

```bash
  python manage.py createsuperuser
```

- Run the server to ensure setup is working:

```bash
  python manage.py runserver
```






