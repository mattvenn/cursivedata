#!/usr/bin/python
import requests
import json
import datetime
import pprint
import argparse

def delete_trigger(id):
    headers= {'content-type': 'application/json', "X-ApiKey": key }
    r = requests.delete(args.url + "/" + str(id) ,headers=headers)
    print r.status_code


def get_triggers():
    headers= {'content-type': 'application/json', "X-ApiKey": key }
    r = requests.get(args.url,headers=headers)
    print r.status_code
    try:
        pprint.pprint(json.loads(r.text))
    except:
        print r.text
    return json.loads(r.text)


if __name__ == '__main__':

    default_url = 'http://api.cosm.com/v2/triggers/'

    parser = argparse.ArgumentParser(description="manage triggers")
    parser.add_argument('--key-file', required=True,
        action='store', dest='key_file', help="key file")
    parser.add_argument('--url',
        action='store', dest='url', default=default_url,
        help="url of the api")
    parser.add_argument('--delete',
        action='store', type=int, dest='delete', 
        help="id to delete")
    parser.add_argument('--delete-all',
        action='store_const', const=True, default=False, dest='delete_all', help="delete all triggers")

    args = parser.parse_args()
    key = open(args.key_file).read()
    print args.url

    triggers = get_triggers()
    if args.delete:
        for trigger in triggers:
            if trigger["id"] == args.delete:
                print "found it", trigger
                delete_trigger(args.delete)

    if args.delete_all:
        for trigger in triggers:
            print "delete trigger", trigger["id"]
            delete_trigger(trigger["id"])

