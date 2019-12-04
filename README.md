# Django Rest Framework Demo (Agile)

[![Requirements Status](https://requires.io/github/Keats/django-drf-template/requirements.png?branch=master)](https://requires.io/github/Keats/django-drf-template/requirements/?branch=master)

Project template for Django 2.2+ Django REST framework containing things I use and find useful.  
Part of it is based on [Two Scoops of Django template](https://github.com/twoscoops/django-twoscoops-project).  

## Features

It contains the following things: 

- [Django](https://www.djangoproject.com/): The web framework for the project
- [Django REST framework](http://www.django-rest-framework.org/): for writing your API
- [django-model-utils](https://django-model-utils.readthedocs.org/en/latest/): for things like TimestampedModel and other nice things for models
- [django-cors-headers](https://github.com/ottoyiu/django-cors-headers): automatically allows CORS on local dev and allows for a whitelist in production

## Install
You will need MySQL installed and the following ones (for ubuntu/debian, for others systems look in your package managers).

```bash
$ sudo apt-get update
$ sudo apt-get install python-pip python-dev mysql-server  libmysqlclient-dev
```

### Create the PostgreSQL Database and User

We’re going to jump right in and create a database and database user for our Django application.

By default, Postgres uses an authentication scheme called “peer authentication” for local connections. Basically, this means that if the user’s operating system username matches a valid Postgres username, that user can login with no further authentication.

During the Postgres installation, an operating system user named postgres was created to correspond to the postgres PostgreSQL administrative user. We need to use this user to perform administrative tasks. We can use sudo and pass in the username with the -u option.

Log into an interactive Postgres session by typing:

```bash
$ sudo -u postgres psql
postgres=# CREATE DATABASE django_backend;
postgres=# CREATE USER user WITH PASSWORD 'password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE django_backend TO user;
postgres=# \q
```

### Create and Configure a New Django Project

Create your virtualenv (examples will use virtualenvwrapper), I will use the name myproject but use your own name.

```bash
$ mkdir agile_drf_demo && cd agile_drf_demo
$ virtualenv venv
$ source venv/bin/activate
$ git clone https://github.com/agileinfoways/Agile-DRF-Demo.git agile_drf_demo
$ cd agile_drf_demo
$ pip install -r requirements.txt
$ cd agile_drf_demo
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
```

By default it will not stop commits because of warning, a quick look at .git/hooks/pre-commit shows that putting an environment variable of FLAKE8_STRICT will stop them.  


And with all that, you should be almost good to go. 
There are a few hardcoded temporary settings that you will want to replace, look for the string 'Ann Onymous' and you should find them.  