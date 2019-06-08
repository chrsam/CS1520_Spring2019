# Store all data in this application (login and listings)
# Be sure to change the projectID when switching domain name

import datetime
import carpool_listing

from google.cloud import datastore
from google.cloud.datastore.key import Key
from carpool_listing import CarPoolListing

CPL_ENTITY_TYPE = 'CarPoolListing'
USER_ENTITY = 'CarPoolUser'
PROJECT_ID = 'pittrideshare'


def log(msg):
    """Log a simple message."""
    print('cpldata: %s' % msg)


def convert_to_object(entity):
    """Convert the entity returned by datastore to a normal object"""
    cpl_id = entity.key.id_or_name
    return CarPoolListing(cpl_id, entity['start_destination'], entity['end_destination'], entity['start_date'], entity['end_date'], entity['description'], entity['seats_available'], entity['contact_info'])


def load_key(client, entity_type, entity_id=None, parent_key=None):
    """Load a datastore key using a particular client, and if known, the ID"""
    key = None
    if entity_id:
        key = client.key(entity_type, entity_id, parent=parent_key)
    else:
        # this will generate a new ID
        key = client.key(entity_type)
    return key


def load_entity(client, entity_type, entity_id, parent_key=None):
    """Load a datastore entity using a particular client, and the ID."""
    key = load_key(client, entity_type, entity_id, parent_key)
    entity = client.get(key)
    log('retrieved entity for ' + str(entity_id))
    return entity

#
# Below is code for datastorage for listings
#


def create_list_item(car_pool_listing, username):
    """Create a new car pool listing item entity from the speicifed object."""
    client = datastore.Client(PROJECT_ID)
    key = load_key(client, CPL_ENTITY_TYPE)
    car_pool_listing.id = key.id_or_name
    entity = datastore.Entity(key)
    entity['username'] = username
    entity['start_destination'] = car_pool_listing.start_destination
    entity['end_destination'] = car_pool_listing.end_destination
    entity['start_date'] = car_pool_listing.start_date
    entity['end_date'] = car_pool_listing.end_date
    entity['description'] = car_pool_listing.description
    entity['seats_available'] = car_pool_listing.seats_available
    entity['contact_info'] = car_pool_listing.contact_info
    client.put(entity)
    log('saved new entity for ID: %s' % key.id_or_name)


def save_list_item(car_pool_listing):
    """Save an existing list item from an object."""
    client = datastore.Client(PROJECT_ID)
    entity = load_entity(client, car_pool_listing.id)
    entity.update(car_pool_listing.to_dict())
    client.put(entity)
    log('entity saved for ID: %s' % car_pool_listing.id)


def get_listings():
    """Load all of the listings."""
    client = datastore.Client(PROJECT_ID)
    q = client.query(kind=CPL_ENTITY_TYPE)
    result = []
    for listing in q.fetch():
        result.append(listing)
    return result


def delete_list_item(cpl_id):
    client = datastore.Client(PROJECT_ID)
    with client.transaction():
        cpl_key = client.key('CarPoolListing', cpl_id)
        log('key loaded for ID: %s' % cpl_id)
        client.delete(cpl_key)
        log('key deleted for ID: %s' % cpl_id)
# def display_list_item(car_pool_list, key):
# search for entity by phone number/id, send post request with XMLHttpRequest

#
# Below is code for datastorage for users/accounts
#


def load_user(username, passwordhash):
    """Load a user based on the passwordhash"""
    client = datastore.Client(PROJECT_ID)
    q = client.query(kind=USER_ENTITY)
    q.add_filter('username', '=', username)
    q.add_filter('passwordhash', '=', passwordhash)
    for user in q.fetch():
        return carpool_listing.User(user['username'], user['email'])
    return None


def load_about_user(username):
    """Return a string that represents the "About Me" information a user has
    stored."""
    client = datastore.Client(PROJECT_ID)
    user = load_entity(client, USER_ENTITY, username)
    if user:
        return user['about']
    else:
        return ''


def save_user(user, passwordhash):
    """Save the user details to the datastore."""
    client = datastore.Client(PROJECT_ID)
    entity = datastore.Entity(load_key(client, USER_ENTITY, user.username))
    entity['username'] = user.username
    entity['email'] = user.email
    entity['about'] = ''
    entity['passwordhash'] = passwordhash
    client.put(entity)


def save_about_user(username, about):
    """Save the user's about info to the datastore."""
    client = datastore.Client(PROJECT_ID)
    user = load_entity(client, USER_ENTITY, username)
    user['about'] = about
    client.put(user)


def get_user_listings(username):
    """Load listings based on the username id."""
    client = datastore.Client(PROJECT_ID)
    q = client.query(kind=CPL_ENTITY_TYPE)
    q.add_filter('username', '=', username)
    result = []
    for listing in q.fetch():
        result.append(listing)
    return result


def user_exists_check(username):
    client = datastore.Client(PROJECT_ID)
    q = client.query(kind=USER_ENTITY)
    q.add_filter('username', '=', username)
    result = None
    for user in q.fetch():
        result = user
    return result
