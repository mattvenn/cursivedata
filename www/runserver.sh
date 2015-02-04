#!/bin/bash

source /home/polarsite/.virtualenvs/polarsite/bin/activate

cd /home/polarsite/cursivedata/www/
exec gunicorn www.wsgi:application -b localhost:8000
