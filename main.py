import webapp2
import os
import jinja2
import time

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'views')
#static_path = os.path.join(os.path.dirname(__file__), "static")
jinja_environment = \
    jinja2.Environment(autoescape=True, extensions=['jinja2.ext.autoescape'], loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

class BaseHandler(webapp2.RequestHandler):
	@webapp2.cached_property
	def auth(self):
		"""Shortcut to access the auth instance as a property."""
		return auth.get_auth()

	@webapp2.cached_property
	def user_info(self):
		"""Shortcut to access a subset of the user attributes that are stored
		in the session.
		The list of attributes to store in the session is specified in
		  config['webapp2_extras.auth']['user_attributes'].
		:returns
		  A dictionary with most user information
		"""
		return self.auth.get_user_by_session()

	@webapp2.cached_property
	def user(self):
		"""Shortcut to access the current logged in user.
		Unlike user_info, it fetches information from the persistence layer and
		returns an instance of the underlying model.
		:returns
		  The instance of the user model associated to the logged in user.
		"""
		u = self.user_info
		return self.user_model.get_by_id(u['user_id']) if u else None

	@webapp2.cached_property
	def user_model(self):
		"""Returns the implementation of the user model.
		It is consistent with config['webapp2_extras.auth']['user_model'], if set.
		"""    
		return self.auth.store.user_model

	@webapp2.cached_property
	def session(self):
		"""Shortcut to access the current session."""
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

# Main page Handlers
# --- Main Page ---#
class MainHandler(BaseHandler):
    def get(self):
        active_home = "active"
        active_settings = ""
        params = {
        'active_home': active_home,
        'active_settings': active_settings
        }
        self.render_template('index.html', params)



app = webapp2.WSGIApplication([
	webapp2.Route('/', MainHandler, name='home')
	], debug=True)