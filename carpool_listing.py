# Stores all data in this application (login and listings)


class CarPoolListing(object):
    def __init__(self, cpid, start_destination, end_destination, start_date, end_date, description, seats_available, contact_info):
        self.id = cpid
        self.start_destination = start_destination
        self.end_destination = end_destination
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.seats_available = seats_available
        self.contact_info = contact_info

    def to_dict(self):
        return {
          'start_destination': self.start_destination,
          'end_destination': self.end_destination,
          'start_date': self.start_date,
          'end_date': self.end_date,
          'description': self.description,
          'seats_available': self.seats_available,
          'contact_info': self.contact_info
        }


class User(object):
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
        }
