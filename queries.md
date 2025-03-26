total number of items
```json
[
    {
        "$match": {
            "$and": [
                {
                    "status": {
                        "$in": [
                            "Available",
                            "Out for Repairs",
                            "Checked Out"
                        ]
                    }
                },
                {
                    "$or": [
                        {
                            "resource.name": {
                                "$in": [
                                    "Dell Inc. Latitude 3120"
                                ]
                            }
                        },
                        {
                            "resource.name": {
                                "$regex": ".*chromebook.*",
                                "$options": "i"
                            }
                        }
                    ]
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "$site.guid",
            "count": {
                "$sum": 1
            }
        }
    },
    {
        "$lookup": {
            "from": "sites",
            "localField": "_id",
            "foreignField": "guid",
            "as": "school"
        }
    },
    {
        "$unwind": "$school"
    },
    {
        "$project": {
            "_id": 0,
            "count": 1,
            "name": "$school.name"
        }
    },
    {
        "$sort": {
            "name": 1
        }
    }
]
```
total fines
```json
[
    {
        "$match": {
            "$and": [
                {
                    "site.shortName": {
                        "$in": [${school:doublequote}]
                    }
                },
                {
                    "patron.grade": {
                        "$in": [${grade:doublequote}]
                    }
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "id",
            "total": {
                "$sum":"$fine.amount"
            }
        }
    }
]
```
fines by patron
```json
[
    {
        "$match": {
            "$and": [
                {
                    "site.shortName": {
                        "$in": [${school:doublequote}]
                    }
                },
                {
                    "patron.grade": {
                        "$in": [${grade:doublequote}]
                    }
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "$patron",
            "total": {
                "$sum": "$fine.amount"
            }
        }
    },
    {
        "$sort": {
            "total": -1
        }
    },
    {
        "$project": {
            "Total fines": "$total",
            "First name": "$_id.firstName",
            "Last name": "$_id.lastName"
        }
    }
]
```
number of fines by resource
```json
[
    {
        "$match": {
            "$and": [
                {
                    "site.shortName": {
                        "$in": [${school:doublequote}]
                    }
                },
                {
                    "patron.grade": {
                        "$in": [${grade:doublequote}]
                    }
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "$item.name",
            "total": {
                "$sum": 1
            }
        }
    }
]
```
number of fines by grade
```json
[
    {
        "$match": {
            "$and": [
                {
                    "site.shortName": {
                        "$in": [${school:doublequote}]
                    }
                },
                {
                    "patron.grade": {
                        "$in": [${grade:doublequote}]
                    }
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "$patron.grade",
            "total": {
                "$sum": 1
            }
        }
    }
]
```
total fines by school
```json
[
    {
        "$match": {
            "$and": [
                {
                    "site.shortName": {
                        "$in": [${school:doublequote}]
                    }
                },
                {
                    "patron.grade": {
                        "$in": [${grade:doublequote}]
                    }
                }
            ]
        }
    },
    {
        "$group": {
            "_id": "$site.shortName",
            "total": {
                "$sum": "$fine.amount"
            }
        }
    }
]
```