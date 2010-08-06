#usual
import os
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


#i18n stuff
os.environ['DJANGO_SETTINGS_MODULE'] = 'conf.settings'
from django.conf import settings
settings._target = None
import i18nutil

class MainPage(i18nutil.I18NRequestHandler):

	def get(self):           
		
		template_values = {}		
		
		path = os.path.join(os.path.dirname(__file__), 'html5.html')
		self.response.out.write(template.render(path, template_values))
		
application = webapp.WSGIApplication(
						[('/', MainPage)],
						debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()