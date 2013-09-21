from google.appengine.ext import ndb
import logging


#
# User
#
# Provides an abstraction layer around user registration. This is necessary to allow
# links to be sent to unregistered users. The key for a registered user will be
# the id from an AppEngine User object (i.e. google.appengine.api.users.User.user_id()). 
# The User object being defined in this module is the only one the application should 
# ever reference. It is responsible for keeping the mapping to the 
# google.appengine.api.users.User object.
#
class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)


class SharedLink(ndb.Model):
    url = ndb.StringProperty(required=True)
    title = ndb.StringProperty()
    favicon = ndb.StringProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    read = ndb.BooleanProperty(required=True, default=False)
    comment = ndb.StringProperty()


class Friend(ndb.Model):
    user = ndb.StructuredProperty(User, required=True)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)


def getLinkByUrlsafeId(id):
    k = ndb.Key(urlsafe=id)
    return k.get()