#!/usr/bin/env python

import csv, requests
from datetime import datetime
from pymongo import MongoClient

import config
from follett_client import DestinyClient

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
    mongo.destiny.info.update_one({'_id': 'in_progress'}, {'$set': {'value': True}}, upsert=True)

    print('Inserting fines', flush=True)

    # clear collections
    collection_fines = mongo.destiny.fines
    collection_fines.drop()

    # get fines
    fines = destiny.get_fines()
    for fines_item in fines:
        patron = destiny.get_patron(fines_item['patron']['guid'])
        for fine in fines_item['fines']:
            insert = {
                'site': {
                    'name': fines_item['site']['name'],
                    'shortName': fines_item['site']['shortName']
                },
                'patron': {
                    'barcode': fines_item['patron']['barcode'],
                    'firstName': fines_item['patron']['firstName'],
                    'middleName': fines_item['patron']['middleName'],
                    'lastName': fines_item['patron']['lastName'],
                },
                'fine': {
                    'description': fine['description'],
                    'amount': fine['paymentSummary']['amountDue'],
                    'date': datetime.fromisoformat(fine['dateCreated']),
                    'type': fine['type']
                }
            }

            # for fines not attached to an item
            try:
                insert['item'] = {
                    'name': fine['bib']['title']
                }
            except:
                pass

            # add grade level to fine
            if 'gradeLevel' in patron:
                insert['patron']['grade'] = patron['gradeLevel']
            else:
                insert['patron']['grade'] = 'N/A'

            collection_fines.insert_one(insert)

    # clear sites collection
    collection_sites = mongo.destiny.sites
    collection_sites.drop()

    # get sites
    sites = destiny.get_sites()
    sites['value'][0]
    collection_sites.insert_many(sites['value'])

    # clear items collection
    collection_items = mongo.destiny.items
    collection_items.drop()

    # get resource types
    types = destiny.get_resourcetypes()
    # get top level technology type
    root = types['children'][4]

    get_items_recurse(root=root, destiny=destiny, collection=collection_items)

    # get enrollment numbers
    enrollment_request = requests.get(config.ENROLLMENT_URL)
    collection_enrollment = mongo.destiny.enrollment
    collection_enrollment.drop()

    enrollment_reader = csv.DictReader(enrollment_request.text.replace(' ','').split('\n'))
    for school in enrollment_reader:
        abbr = school.pop('abbreviation')
        for grade, count in school.items():
            collection_enrollment.insert_one({
                'school': abbr,
                'grade': int(grade) if grade.isnumeric() else 0,
                'count': int(count)
            })

    # get final counts
    collection_final = mongo.destiny.final
    collection_final.drop()
    for site in config.ABBR_MAP:
        inserting = {
            'school': site['name'],
            'abbreviation': site['abbreviation'],
            'location': site['location'],
            'items': collection_items.count_documents(dict(
                {
                    'status': {
                        '$in': [
                            'Available',
                            'Checked Out'
                        ]
                    }
                },
                **site['items']
            )),
            'enrollment': list(collection_enrollment.aggregate([
                {
                    '$match': site['enrollment']
                },
                {
                    '$group': {
                        '_id': None,
                        'count': {
                            '$sum': '$count'
                        }
                    }
                }
            ]))[0]['count']
        }

        collection_final.insert_one(inserting)

    mongo.destiny.info.update_one({'_id': 'in_progress'}, {'$set': {'value': False}})