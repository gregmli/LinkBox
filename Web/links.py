#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import logging
import linkdb
import json
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
logger = logging.getLogger(__name__)

def parseToField(text):
    emailPrefix = 'mailto:'

    if text is None or len(text) == 0:
        return None

    recipients = text.split(',')

    def processRecipients(r):
        if (r.startswith(emailPrefix)):
            email = r[len(emailPrefix):]
            return email
        else:
            id = r
            k = ndb.Key(urlsafe=id)
            user = k.get()
            return user

    out = map(processRecipients, recipients)
    return out

def checkLoggedIn(requestHandler):
    user = users.get_current_user()

    if not user:
        # for API calls, do a 401 error code. This signals to the API user
        # to login
        requestHandler.abort(401)

        # todo: in future, for UI requests, redirect to a login form

        return

    else:
        # fetch or create the user from the datastore
        userObj = linkdb.User.get_or_insert(user.user_id(), email=user.email())

        return userObj


def createLoginURL(request):
    return "/login"


#
# This is the business logic class for the application. LinkUser encapsulates
# the logic above the data storage layer
#
class LinkUser:
    def __init__(self, user):
        self.user = user

    # shareLink
    #
    # Shares a link with 0 or more recipients
    # 
    # If no recipients are specified, then the link is saved to the current user's
    # inbox. Recipients can contain either email addresses, or user IDs. User IDs
    # should be used between people who have friended each other already. For 
    # recipients who haven't been friended, pass an email address, and an email
    # notification will be sent.
    # 
    def shareLink(self, recipients, url, title, favicon, comment):
    
        if recipients is None or len(recipients) == 0:
            recipients = [self.user]

        links = []
        for r in recipients:
            if isinstance(r, linkdb.User):
                l = linkdb.SharedLink(parent=r.key, url=url, title=title, favicon=favicon, comment=comment, createdBy=self.user)
                
            else:
                l = linkdb.SharedLink(emailRecipient=r, url=url, title=title, favicon=favicon, comment=comment, createdBy=self.user)
                
                try:
                    self.sendEmailShare(r, l)
                except:
                    # TODO: handle exceptions
                    pass

            # l.put()
            links.append(l)

        ndb.put_multi(links)

    def getLinks(self):
        links = linkdb.SharedLink.query(ancestor = self.user.key).order(-linkdb.SharedLink.created)

        def mapToObject(l):
            return {
                'id': l.key.urlsafe(),
                'url': l.url,
                'title': l.title,
                'favicon': l.favicon,
                'comment': l.comment,
                'read': l.read
            }

        out = map(mapToObject, links)

        return out

    def sendEmailShare(self, recipientEmail, link):
        template = jinja_environment.get_template('emailshare.txt')
        text = template.render(link=link)

        message = mail.EmailMessage(
            sender = self.user.email(),
            to = recipientEmail,
            subject = l.title,
            body = text)
                
        message.send()
        
    def markLinkAsRead(self, urlSafeId, read=True):
        logger.info("getting link by '%s'" % urlSafeId)
        k = ndb.Key(urlsafe=urlSafeId)
        link = k.get()
        link.read = read
        link.put()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class LinkHandler(webapp2.RequestHandler):
    def put(self):
        user = checkLoggedIn(self)
        if not user:
            return

        to = self.request.get('to')
        url = self.request.get('url')
        title = self.request.get('title')
        favicon = self.request.get('favicon')
        comment = self.request.get('comment')
        
        lu = LinkUser(user)

        lu.shareLink(None, url, title, favicon, comment)

    def get(self):
        user = checkLoggedIn(self)
        if not user:
            return

        lu = LinkUser(user)

        links = lu.getLinks()

        self.response.write(json.dumps(links))


    def post(self):
        user = checkLoggedIn(self)
        if not user:
            return

        id = self.request.get('id')
        read = self.request.get('read')
        read = not(read in ['', '0', 'false', 'False'])

        lu = LinkUser(user)
        lu.markLinkAsRead(id, read)



class LoginHandler(webapp2.RequestHandler):
    def get(self):
        
        user = users.get_current_user()

        if user:
            # for API calls, just close the browser tab
            template = jinja_environment.get_template('closeme.html')
            self.response.out.write(template.render(action="callback_loggedIn"))

            # todo: in future, for UI requests, redirect to destination page

        else:
            url = users.create_login_url(createLoginURL("/login"))
            self.redirect(url)


class LogoutHandler(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()

        if user:
            url = users.create_logout_url("/logout")
            self.redirect(url)

        else:
            # for API calls, just close the browser tab
            template = jinja_environment.get_template('closeme.html')
            self.response.out.write(template.render(action="callback_loggedOut"))

            # todo: in future, for UI requests, redirect to destination page



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/links', LinkHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
], debug=True)
