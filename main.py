import webapp2
import os
import jinja2
import time

from models import treeSpecies

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'views')
#static_path = os.path.join(os.path.dirname(__file__), "static")
jinja_environment = \
    jinja2.Environment(autoescape=True, extensions=['jinja2.ext.autoescape'], loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def auth(self):
		return	auth.get_auth()

	@webapp2.cached_property
	def user_info(self):
		return self.auth.get_user_by_session()

	@webapp2.cached_property
	def user(self):
		u = self.user_info
		return self.user_model.get_by_id(u['user_id']) if u else None

	def user_model(self):
		return self.auth.store.user_model

	@webapp2.cached_property
	def session(self):
		return self.session_store.get_session(backend="datastore")

	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)

	def render_template(
		self,
		filename,
		template_values,
		**template_args
		):
		template = jinja_environment.get_template(filename)
		self.response.out.write(template.render(template_values))

# Page Handlers
# --- Main Page --- #
class MainHandler(BaseHandler):
	def get(self):
		active_home = "active"
		active_settings = ""
		params = {
		'active_home': active_home,
		'active_settings': active_settings
		}
		self.render_template('index.html', params)

# --- Species Main Page --- #
class SpeciesHandler(BaseHandler):
	def get(self):
		speciesList = treeSpecies.query().order(treeSpecies.speciesName)
		params = {
		'speciesList': speciesList
		}
		self.render_template('species.html', params)


	def post(self):
		tSpecies = treeSpecies(speciesName=self.request.get('speciesName'),
		treeType=self.request.get('treeType'),
		treeDesc=self.request.get('treeDesc'),
		leafPic=self.request.get('leafPic'),
		fruitPic=self.request.get('fruitPic'))
		tSpecies.put()
		return self.redirect('species')

app = webapp2.WSGIApplication([
	webapp2.Route('/', MainHandler, name='home'),
	webapp2.Route('/admin/species', SpeciesHandler, name='species')
	], debug=True)