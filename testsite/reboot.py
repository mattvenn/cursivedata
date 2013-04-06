import os

from polargraph.scripts import *

#start from a blank db
#os.system("rm db/testsite.sqlite; python manage.py syncdb --noinput; python manage.py createsuperuser --noinput --username=admin --email=a@b.com")
os.system("mysqldump -upolargraph -ppolargraph polargraph > db/db.$(date +%y%m%d)")
os.system("mysql -upolargraph -ppolargraph -e 'drop database polargraph ; create database polargraph'")
os.system("python manage.py syncdb --noinput; python manage.py createsuperuser --noinput --username=admin --email=a@b.com")

#remove all old data files
os.system("find data/ -type f ! -name initial | xargs rm")

#create a pipeline and some generators
test_creating_pipeline()
