from google.appengine.ext import ndb
import logging


#
# User
#  + SharedLink
#  + Friend
#
# The User object is the parent of both SharedLink and Friend. A User object represents
# both registered and unregistered users. Friend relationships are created automatically
# whenever one user shares a link with another. Because they are automatically created,
# the block property on the relationship is used to block unwanted link sharing.
#

#
# User
#
# Provides an abstraction layer around user registration. This is necessary to allow
# links to be sent to unregistered users. The key for a registered user will be
# the id from an AppEngine User object (i.e. google.appengine.api.users.User.user_id()). 
# The User object being defined in this module is the only one the application should 
# ever reference. 
#
class User(ndb.Model):
    email = ndb.StringProperty(required=True)
    googleId = ndb.StringProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)


# SharedLink
#
# A SharedLink is parented to the User it was shared with. This makes for easy 
# lookup, as a User's inbox is just all the SharedLinks that belong to it.
#
# For unregistered users, a User object must be created. This is to simplify
# operation when a link is shared with a registered user who is not an existing
# friend.
#  
class SharedLink(ndb.Model):
    url = ndb.StringProperty(required=True)
    title = ndb.StringProperty()
    favicon = ndb.StringProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    read = ndb.BooleanProperty(required=True, default=False)
    comment = ndb.StringProperty()
    createdBy = ndb.StructuredProperty(User, required=True)

# 
# Friend
#
# A one-way relationship between two users. The parent is used to store the user
# who is the owner, while the friend is stored as a property. 
#
# The owner is used as the parent because these lookups are frequent, and need to 
# be done quickly (every time a user needs to autocomplete from the list of friends,
# whereas the only time the reverse lookup is necessary is when the link is shared,
# to actually see who the user is a friend of (and thus whom should receive email
# notifications, versus being directly notified)
#
# The shortname is a human-readable name for the user to use to refer to her friends
#
class Friend(ndb.Model):
    user = ndb.StructuredProperty(User, required=True)
    shortname = ndb.StringProperty()
    blocked = ndb.BooleanProperty(required=True, default=False)
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)

