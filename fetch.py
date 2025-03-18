#!/usr/bin/env python

import config
# import json
from follett_client import DestinyClient
from pymongo import MongoClient

destiny = DestinyClient(config)
mongo = MongoClient()

def get_items_recurse(root, destiny, collection):
    """
    Recursively add all items of a resourcetype and sub-resourcetypes to a collection
    """

    # add all items to the mongodb collection
    print(f'Adding {root['name']}', end='', flush=True)

    # get first page
    page = destiny.get_items(resourcetype=root['guid'])
    print('.', end='', flush=True)

    # loop through middle pages
    while '@nextLink' in page:
        collection.insert_many(page['value'])
        page = destiny.get_next_page(page)
        print('.', end='', flush=True)

    # last page
    if 'value' in page and len(page['value']) > 0:
        collection.insert_many(page['value'])
    print()

    # recurse through child resourcetypes
    if 'children' in root:
        for i in root['children']:
            get_items_recurse(i, destiny, collection)

if __name__ == "__main__":
    # clear sites collection
    collection = mongo.destiny.sites
    collection.drop()

    # get sites
    sites = destiny.get_sites()
    sites['value'][0]
    collection.insert_many(sites['value'])

    # clear items collection
    collection = mongo.destiny.items
    collection.drop()

    # get resource types
    types = destiny.get_resourcetypes()
    # get top level technology type
    root = types['children'][4]

    get_items_recurse(root=root, destiny=destiny, collection=collection)