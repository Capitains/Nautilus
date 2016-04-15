Nautilus' Production Environment deployment advices
===================================================

Environment
###########

We recommend highly to use Debian based configuration as they are the only one having been tested for now. The following configuration takes into account what we think might be the best configuration available with a good cache system.

You can use a `docker image <https://github.com/Capitains/docker-debian-capitains>`_ we built and fork it for your own use. As of *April 11th, 2016*, the **docker image does not use Redis-based cache** but filesystem based cache.

The environment we propose contains a flask.ext.nemo instance, for control purposes. Disabling it is documented.

.. image:: assets/deployment.png
   :alt: Deployment Architecture
   :align: center

Nginx, Supervisor, GUnicorn
###########################

The following configuration file for supervisor is enough for running the whole `nginx <http://nginx.org>`_, `supervisord <http://supervisord.org/>`_ and `gunicorn <http://gunicorn.org/>`_ trio. In general, servers configuration should always - in production - have a trio made of an HTTP/Reverse proxy server such as *nginx*, a process control system such as *supervisor* and a WSGI http server such as *gunicorn* or *uWSGI*. This configuration takes the road of *gunicorn*, but feel free to test and benchmark any combination to know what works best on your own server(s).

On the software is read, run :

.. code-block:: shell

    service supervisor stop
    service nginx stop


Setup
*****

.. code-block:: shell

   apt-get install zlib1g-dev libxslt1-dev libxml2-dev python3 python3-dev python3-pip build-essential nginx supervisor
   apt-get install python-setuptools

   easy_install pip
   pip2.7 install supervisor-stdout
   easy_install3 --upgrade pip

   mkdir /var/capitains-server
   cd /var/capitains-server

   virtualenv venv
   pip install Nautilus
   pip install gunicorn
   pip install flask_nemo

You'll need then to create your own app (You can see below for an example)

Configurations files
********************

.. warning:: These configuration files are designed for the specified directories and services


.. code-block:: ini
   :linenos:
   :caption: /etc/supervisord.conf
   :name: Supervisord configuration

   [supervisord]
   nodaemon = true

   [program:nginx]
   command = /usr/sbin/nginx
   startsecs = 5
   stdout_events_enabled = true
   stderr_events_enabled = true

   [program:app-gunicorn]
   # See explanation for this line
   command=/usr/local/bin/gunicorn app:app -w 4 --threads 2 -b 127.0.0.1:5000 --log-level=debug --pythonpath /usr/bin/python3
   directory=/code
   stdout_events_enabled = true
   stderr_events_enabled = true

   [eventlistener:stdout]
   command = supervisor_stdout
   buffer_size = 100
   events = PROCESS_LOG
   result_handler = supervisor_stdout:event_handler


.. code-block:: nginx
   :linenos:
   :caption: /etc/nginx/nginx.conf
   :name: Nginx configuration

   daemon off;
   error_log /dev/stdout info;
   worker_processes 1;

   # user nobody nogroup;
   pid /tmp/nginx.pid;

   events {
       worker_connections 1024;
       accept_mutex off;
   }

   http {
       include mime.types;
       default_type application/octet-stream;
       access_log /dev/stdout combined;
       sendfile on;

       upstream app_server {
           # For a TCP configuration:
           server 127.0.0.1:5000 fail_timeout=0;
       }

       server {
           listen 80 default;
           client_max_body_size 4G;
           server_name _;

           keepalive_timeout 5;

           # path for static files
           root /opt/app/static;

           location / {
               # checks for static file, if not found proxy to app
               try_files $uri @proxy_to_app;
           }

           location @proxy_to_app {
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header Host $http_host;
               proxy_redirect off;

               proxy_pass   http://app_server;
           }

       }
   }

Flask Application Configuration
###############################

Nemo And FileSystemCache (Easy to maintain)
*******************************************

The following configuration is based on a FileSystemCache. This means that you do not need to install, run and maintain more advanced Cache system such as Redis. This also means this should be slower. The implementation contains a frontend, you should be able to run it without it.

.. code-block:: python
   :linenos:

	# -*- coding: utf-8 -*-

	from flask import Flask, request
	from flask.ext.nemo import Nemo
	from capitains_nautilus.flask_ext import FlaskNautilus
	from werkzeug.contrib.cache import FileSystemCache
	from flask_cache import Cache

	app = Flask("Nautilus")
	nautilus_cache = FileSystemCache("/var/capitains-cache")
	nautilus = FlaskNautilus(
	    app=app,
	    prefix="/api/cts",
	    name="nautilus",
	    # Add here paths to all CapiTainS repository you have locally
	    resources=["/var/capitains-data/canonical-latinLit-master"],
	    parser_cache=nautilus_cache,
	    http_cache=Cache(config={'CACHE_TYPE': "simple"})
	)
	# We set up Nemo
	# This part can be removed 
	nemo = Nemo(
	    app=app,
	    name="nemo",
		base_url="",
		api_url="/api/cts",
	    endpoint=nautilus.retriever
	)
	# We register its routes
	nemo.register_routes()
	# We register its filters
	nemo.register_filters()

	# Removes this line for production
	app.debug = True
	
	if __name__ == "__main__":
	    app.run(debug=True, host='0.0.0.0')