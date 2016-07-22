#!/bin/bash


cd /home/polarsite/cursivedata/www/
source venv/bin/activate
exec gunicorn www.wsgi:application -b localhost:8000 -w 2
