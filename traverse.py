
def parse_json(obj, indent=0):
    for key, value in obj.items():
        if isinstance(value, dict):
            print(' ' * indent + f"{key}:")
            parse_json(value, indent + 2)
        elif isinstance(value, list):
            print(' ' * indent + f"{key}: [")
            for item in value:
                if isinstance(item, dict):
                    parse_json(item, indent + 2)
                else:
                    print(' ' * (indent + 2) + str(item))
            print(' ' * indent + "]")
        else:
            print(' ' * indent + f"{key}: {value}")

# Parse and print the JSON data

data = {
    "name": "Adan",
    "birthMonth": "June",
    "birthPlace": "Kohat, Pakistan",
    "currentLocation": "Pakistan",
    "school": "Booker High School",
    "family": {
        "mother": "Kate",
        "brother": {
            "name": "Jake",
            "ageDifference": 15,
            "relationshipDescription": "sweet kid, fights like cats and dogs"
        },
        "aunt": "Molly"
    },
    "lifePhilosophy": "friends and family who you can trust and who trusts you",
    "emotionalState": {
        "overall": "happy",
        "sadDays": True
    },
    "supportSystem": {
        "friends": True,
        "schoolSupport": True
    },
    "relationshipHistory": {
        "currentRelationship": False,
        "pastBoyfriend": {
            "duration": 29,
            "favoriteActivities": [
                "movies",
                "dinner",
                "beach",
                "Universal Studios"
            ]
        }
    },
    "futureProjection": {
        "year": 2018,
        "livingStatus": "still living in Sarasota",
        "maritalStatus": "married",
        "spouse": {
            "name": "Paul Smith",
            "characteristics": {
                "personality": "sweet",
                "height": "6 feet",
                "physique": "built well",
                "eyeColor": "baby blue",
                "hairColor": "blond"
            }
        },
        "children": {
            "name": "Linda Treasa Smith",
            "age": 3,
            "description": "a little devil"
        }
    },
    "hobbies": [
        "hunting",
        "watching movies",
        "riding"
    ]
}
parse_json(data)