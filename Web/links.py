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

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


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


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


class LinkHandler(webapp2.RequestHandler):
    def put(self):
        user = checkLoggedIn(self)
        if not user:
            return

        url = self.request.get('url')
        title = self.request.get('title')
        favicon = self.request.get('favicon')
        comment = self.request.get('comment')
        
        l = linkdb.SharedLink(parent=user.key, url=url, title=title, favicon=favicon, comment=comment)
        l.put()

    def get(self):
        user = checkLoggedIn(self)
        if not user:
            return

        links = linkdb.SharedLink.query(ancestor = user.key).order(-linkdb.SharedLink.created)

        out = []
        for l in links:

            obj = {
                'id': l.key.urlsafe(),
                'url': l.url,
                'title': l.title,
                'favicon': l.favicon,
                'comment': l.comment,
                'read': l.read
            }
            out.append(obj)

        self.response.write(json.dumps(out))


    def post(self):
        user = checkLoggedIn(self)
        if not user:
            return

        id = self.request.get('id')
        read = self.request.get('read')

        link = linkdb.getLinkByUrlsafeId(id)
        link.read = not(read in ['', '0', 'false', 'False'])
        link.put()




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
