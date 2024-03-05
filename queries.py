def actor_selection(actor_name):
    return [{"$match": {"$text": {"$search": f'"{actor_name}"'}}}]


giga_query = [
    {"$project": {"_id": 1, "primaryName": 1, "birthYear": 1, "deathYear": 1}},
    {
        "$lookup": {
            "from": "title_principal",
            "localField": "_id",
            "foreignField": "nconst",
            "as": "main_actor",
        }
    },
    {"$unwind": {"path": "$main_actor", "preserveNullAndEmptyArrays": False}},
    {
        "$project": {
            "main_actor.nconst": "$_id",
            "main_actor.primaryName": "$primaryName",
            "main_actor.birthYear": "$birthYear",
            "main_actor.deathYear": "$deathYear",
            "main_actor.characters": 1,
            "main_actor.category": 1,
            "tconst": "$main_actor.tconst",
        }
    },
    {
        "$lookup": {
            "from": "title_principal",
            "localField": "tconst",
            "foreignField": "tconst",
            "as": "companion_actor",
        }
    },
    {"$unwind": {"path": "$companion_actor", "preserveNullAndEmptyArrays": False}},
    {"$unset": ["companion_actor._id", "companion_actor.tconst"]},
    {"$match": {"$expr": {"$ne": ["$main_actor.nconst", "$companion_actor.nconst"]}}},
    {
        "$lookup": {
            "from": "name_basics",
            "localField": "companion_actor.nconst",
            "foreignField": "_id",
            "as": "companion_actor_info",
        }
    },
    {"$unwind": {"path": "$companion_actor_info", "preserveNullAndEmptyArrays": False}},
    {
        "$set": {
            "companion_actor_info": {"$mergeObjects": ["$companion_actor", "$companion_actor_info"]}
        }
    },
    {"$unset": ["companion_actor", "companion_actor_info._id"]},
    {
        "$lookup": {
            "from": "title_basics",
            "localField": "tconst",
            "foreignField": "_id",
            "as": "companion_movie",
        }
    },
    {"$unwind": {"path": "$companion_movie", "preserveNullAndEmptyArrays": False}},
    {
        "$group": {
            "_id": "$companion_actor_info.nconst",
            "common_movies": {"$push": "$companion_movie"},
            "main_actor": {"$first": "$main_actor"},
            "count": {"$count": {}},
            "ca_nconst": {"$first": "$companion_actor_info.nconst"},
            "ca_category": {"$push": "$companion_actor_info.category"},
            "ca_characters": {"$push": "$companion_actor_info.characters"},
            "ca_primaryName": {"$first": "$companion_actor_info.primaryName"},
            "ca_birthYear": {"$first": "$companion_actor_info.birthYear"},
            "ca_deathYear": {"$first": "$companion_actor_info.deathYear"},
            "ca_primaryProfession": {"$first": "$companion_actor_info.primaryProfession"},
        }
    },
    {
        "$project": {
            "_id": 1,
            "common_movies": 1,
            "main_actor": 1,
            "count": 1,
            "companion_actor.nconst": "$ca_nconst",
            "companion_actor.category": "$ca_category",
            "companion_actor.characters": "$ca_characters",
            "companion_actor.primaryName": "$ca_primaryName",
            "companion_actor.birthYear": "$ca_birthYear",
            "companion_actor.deathYear": "$ca_deathYear",
            "companion_actor.primaryProfession": "$ca_primaryProfession",
        }
    },
]


def actor_relations_query(actor_name):
    return actor_selection(actor_name) + giga_query


def get_actor_relations(actor_name, db):
    pipeline = actor_relations_query(actor_name)
    return list(db["name_basics"].aggregate(pipeline))
