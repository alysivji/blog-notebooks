fitness_api = {}


def motivation_message(person_id):
    user = fitness_api.get('user/', params={'user': person_id})
    name = user[0].get('name')

    activities = fitness_api.get('activity/', params={'user': person_id})
    total_distance = 0
    for activity in activities:
        total_distance += activity.get('distance')

    return f'{name} has run {total_distance} miles'
