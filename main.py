import webapp2
import os
import jinja2
import time
import webapp2_extras.appengine.auth.models
import logging

from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from webapp2_extras import security
from models import treeSpecies, User, treePlot

def user_required(handler):
	"""
	Decorator that checks if there's a user associated with the current session.
	Will also fail if there's no session present.
	"""
	def check_login(self, *args, **kwargs):
		auth = self.auth
		if not auth.get_user_by_session():
			self.redirect(self.uri_for('login'), abort=True)
		else:
			return handler(self, *args, **kwargs)

	return check_login

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

	@webapp2.cached_property
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

	def dispatch(self):
      # Get a session store for this request.
		self.session_store = sessions.get_store(request=self.request)

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			# Save all sessions.
			self.session_store.save_sessions(self.response)

	def display_message(self, message):
		"""Utility function to display a template with a simple message."""
		params = {
		'message': message
		}
		self.render_template('message.html', params)

class LoginHandler(BaseHandler):
	def get(self):
		self._serve_page()

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		try:
			u = self.auth.get_user_by_password(username, password, remember=True, save_session=True)
			self.redirect(self.uri_for('home'))
		except (InvalidAuthIdError, InvalidPasswordError) as e:
			logging.info('Login failed for user %s because of %s', username, type(e))
			self._serve_page(True)

	def _serve_page(self, failed=False):
		username = self.request.get('username')
		params = {
		'username': username,
		'failed': failed}
		self.render_template('login.html', params)

class LogoutHandler(BaseHandler):
	def get(self):
		self.auth.unset_session()
		self.redirect(self.uri_for('home'))

class AuthenticatedHandler(BaseHandler):
	def get(self):
		self.render_template('authenticated.html')

class SignupHandler(BaseHandler):
	def get(self):
		u = self.user_info
		username = u['name'] if u else None
		params = {'username': username}
		self.render_template('signup.html', params)

	def post(self):
		user_name = self.request.get('username')
		email = self.request.get('email')
		name = self.request.get('name')
		password = self.request.get('password')
		last_name = self.request.get('lastname')

		unique_properties = ['email_address']
		user_data = self.user_model.create_user(user_name, unique_properties,
			email_address=email, name=name, password_raw=password,
			last_name=last_name, verified=False)
		if not user_data[0]: #user_data is a tuple
			self.display_message('Unable to create user for email %s because of \
			duplicate keys %s' % (user_name, user_data[1]))
		return
    
		user = user_data[1]
		user_id = user.get_id()
		token = self.user_model.create_signup_token(user_id)
		verification_url = self.uri_for('verification', type='v', user_id=user_id,
			signup_token=token, _full=True)

		msg = 'Send an email to user in order to verify their address. \
		      They will be able to do so by visiting <a href="{url}">{url}</a>'

		self.display_message(msg.format(url=verification_url))

class ForgotPasswordHandler(BaseHandler):
	@user_required
	def get(self):
		self._serve_page()

 	def post(self):
 		username = self.request.get('username')

		user = self.user_model.get_by_auth_id(username)
		if not user:
			logging.info('Could not find any user entry for username %s', username)
			self._serve_page(not_found=True)
		return

		user_id = user.get_id()
		token = self.user_model.create_signup_token(user_id)
		verification_url = self.uri_for('verification', type='p', user_id=user_id,
			signup_token=token, _full=True)

		msg = 'Send an email to user in order to reset their password. \
		They will be able to do so by visiting <a href="{url}">{url}</a>'
		self.display_message(msg.format(url=verification_url))

	def _serve_page(self, not_found=False):
		username = self.request.get('username')
		params = {
		'username': username,
		'not_found': not_found
		}
		self.render_template('forgot.html', params)


class VerificationHandler(BaseHandler):
	def get(self, *args, **kwargs):
		user = None
		user_id = kwargs['user_id']
		signup_token = kwargs['signup_token']
		verification_type = kwargs['type']

    # it should be something more concise like
    # self.auth.get_user_by_token(user_id, signup_token
    # unfortunately the auth interface does not (yet) allow to manipulate
    # signup tokens concisely
		user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,'signup')

		if not user:
			logging.info('Could not find any user with id "%s" signup token "%s"',
			user_id, signup_token)
			self.abort(404)
    
    # store user data in the session
		self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

		if verification_type == 'v':
			# remove signup token, we don't want users to come back with an old link
			self.user_model.delete_signup_token(user.get_id(), signup_token)

		if not user.verified:
			user.verified = True
			user.put()

			self.display_message('User email address has been verified.')
			return
		elif verification_type == 'p':
			# supply user to the page
			params = {
			'user': user,
			'token': signup_token
			}
			self.render_template('resetpassword.html', params)
		else:
			logging.info('verification type not supported')
			self.abort(404)

class SetPasswordHandler(BaseHandler):

	#@user_required
	def post(self):
		password = self.request.get('password')
		old_token = self.request.get('t')

		if not password or password != self.request.get('confirm_password'):
			self.display_message('passwords do not match')
			return

		user = self.user
		user.set_password(password)
		user.put()

		# remove signup token, we don't want users to come back with an old link
		self.user_model.delete_signup_token(user.get_id(), old_token)

		self.display_message('Password updated')

config = {
	'webapp2_extras.auth': {
	'user_model': 'models.User',
	'user_attributes': ['name']
	},
	'webapp2_extras.sessions': {
	'secret_key': 'YOUR_SECRET_KEY'
	}
	}

# Page Handlers
# --- Main Page --- #
class MainHandler(BaseHandler):
	def get(self):
		plotList = treePlot.query().order(treePlot.mDate) 
		params = {
		'plotList': plotList,
		}
		self.render_template('index.html', params)

# --- Species Main Page --- #
class SpeciesHandler(BaseHandler):
	@user_required
	def get(self):
		speciesList = treeSpecies.query().order(treeSpecies.speciesName)
		params = {
		'speciesList': speciesList
		}
		self.render_template('species.html', params)
		
class PlotHandler(BaseHandler):
	def get(self):
		param_item =""
		params = {
		'para_item': para_item
		}
		self.render_template('plot.html', params)
		


	def post(self):
		tSpecies = treeSpecies(speciesName=self.request.get('speciesName'),
		treeType=self.request.get('treeType'),
		treeDesc=self.request.get('treeDesc'),
		leafPic=self.request.get('leafPic'),
		fruitPic=self.request.get('fruitPic'))
		tSpecies.put()
		return self.redirect('species')

app = webapp2.WSGIApplication([
	webapp2.Route('/signup', SignupHandler, name='signup'),
	webapp2.Route('/login', LoginHandler, name='login'),
	webapp2.Route('/logout', LogoutHandler, name='logout'),
	webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
      handler=VerificationHandler, name='verification'),
	webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated'),
	webapp2.Route('/', MainHandler, name='home'),
	webapp2.Route('/admin/species', SpeciesHandler, name='species')
	], debug=True, config=config)