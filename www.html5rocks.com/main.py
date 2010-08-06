# Copyright 2010 Google Inc.
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

# Standard Imports
import datetime
import os
import logging

# Libraries
import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer

# Google App Engine Imports
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from django.utils import feedgenerator

webapp.template.register_template_library('templatefilters')

#i18n stuff
os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
settings._target = None
import i18nutil

class ContentHandler(i18nutil.I18NRequestHandler):

  def get_toc(self, path):
    toc = memcache.get('toc|%s' % path)
    if toc is None or self.request.cache == False:
      template_text = webapp.template.render(path, {});
      parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
      dom_tree = parser.parse(template_text)
      walker = treewalkers.getTreeWalker("dom")
      stream = walker(dom_tree)
      toc = []
      current = None
      for element in stream:
        if element['type'] == 'StartTag':
          if element['name'] in ['h2', 'h3', 'h4']:
            for attr in element['data']:
              if attr[0] == 'id':
                current = {
                  'level' : int(element['name'][-1:]) - 1,
                  'id' : attr[1]
                }
        elif element['type'] == 'Characters' and current is not None:
          current['text'] = element['data']
        elif element['type'] == 'EndTag' and current is not None:
          toc.append(current)
          current = None
      memcache.set('toc|%s' % path, toc, 3600)
    return toc

  def get_feed(self, path):
    articles = memcache.get('feed|%s' % path)
    if articles is None or self.request.cache == False:
      template_text = webapp.template.render(path, {});
      parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
      dom_tree = parser.parse(template_text)
      walker = treewalkers.getTreeWalker("dom")
      stream = walker(dom_tree)

      def __get_attr(element, attr):
        for a in element['data']:
          if a[0] == attr:
            return a[1]
        return None

      articles = []
      article = None

      for element in stream:
        if element['type'] == 'StartTag':
          if element['name'] in ['h2']:
            article = {}
            article['id'] = __get_attr(element, 'id')
            article['pubdate'] = __get_attr(element, 'data-pubdate')
            if article['pubdate'] is not None:
              article['pubdate'] = datetime.datetime.strptime(
                  article['pubdate'], '%Y-%m-%d')
          if element['name'] == 'a' and article is not None:
            article['href'] = __get_attr(element, 'href')
        elif element['type'] == 'Characters' and article is not None:
          article['title'] = element['data']
        elif element['type'] == 'EndTag' and article is not None:
          articles.append(article)
          article = None
      logging.info(articles)
      memcache.set('feed|%s' % path, articles, 3600)
    return articles

  def render(self, data={}, template_path=None, status=None, message=None):
    if status is not None and status != 200:
      logging.error(message)
      self.response.set_status(status, message)
      self.response.out.write(message)
      return

    template_data = {
      'toc' : self.get_toc(template_path),
      'self_url': self.request.url,
      'host': '%s://%s' % (self.request.scheme, self.request.host)
    }

    # Request was for an Atom feed. Render one!
    if self.request.path.endswith('.xml'):
      self.render_atom_feed(template_path, self.get_feed(template_path))
      return

    template_data.update(data)
    self.response.headers.add_header('Content-Type', 'text/html;charset=UTF-8')
    # self.response.headers.add_header("X-UA-Compatible","IE=Edge,chrome=1")
    self.response.out.write(
        webapp.template.render(template_path, template_data))

  def render_atom_feed(self, template_path, data):
    prefix = self.request.url[:self.request.url.rfind('/') + 1]
    logging.info(prefix)
    feed = feedgenerator.Atom1Feed(
        title=u'HTML5Rocks - Tutorials',  # TODO: make generic for any page.
        link=prefix,
        description=u'Take a guided tour through code that uses HTML5.',
        language=u'en'
        )
    for tutorial in data:
      feed.add_item(
          title=tutorial['title'],
          link=prefix + tutorial['href'],
          description=u'',  # TODO: parse this out out of the html and fill it.
          pubdate=tutorial['pubdate']
          )
    self.response.headers.add_header('Content-Type', 'application/atom+xml')
    self.response.out.write(feed.writeString('utf-8'))

  def get(self, relpath):
    if self.request.get('cache', '1') == '0':
      self.request.cache = False
    else:
      self.request.cache = True

    basedir = os.path.dirname(__file__)

    logging.info(relpath)

    if relpath == '' or relpath[-1:] == '/':  # Landing page.
      path = os.path.join(basedir, 'content', relpath, 'index.html')
    else:
      path = os.path.join(basedir, 'content', relpath)

    # Render the .html page if it exists. Otherwise, check that the Atom feed
    # the user is requesting jas a corresponding .html page that exists.
    logging.info(path)
    if os.path.isfile(path):
      self.render(template_path=path)
    elif os.path.isfile(path[:path.rfind('.')] + '.html'):
      self.render(template_path=path[:path.rfind('.')] + '.html')
    else:
      self.render(status=404, message='Sample not found')


def main():
  application = webapp.WSGIApplication([
    ('/(.*)', ContentHandler)
  ], debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
