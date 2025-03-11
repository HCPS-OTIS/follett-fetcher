#!/usr/bin/env python

import config
# import json
from follett_client import DestinyClient
from pymongo import MongoClient

destiny = DestinyClient(config)
mongo = MongoClient()

def copy_id_to_id(item):
    item['_id'] = item['id']
    return item

if __name__ == "__main__":
    # clears collection
    collection = mongo.destiny.items
    collection.drop()

    # gets all items (at around 8/second)
    page = destiny.get_items()
    while (page['@nextLink']):
        print('inserting ' + ', '.join([str(item['id']) for item in page['value']]))
        collection.insert_many([item for item in page['value']])
        page = destiny.get_next_page(page)