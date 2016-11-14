from google.appengine.ext import ndb
from webapp2_extras import sessions
from webapp2_extras import auth
from webapp2_extras import security

import webapp2_extras.appengine.auth.models
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import logging
import os.path
import webapp2
import time

class User(webapp2_extras.appengine.auth.models.User):
	def set_password(self, raw_password):
		"""Sets the password for the current user

		:param raw_password:
		The raw password which will be hashed and stored
		"""
		self.password = security.generate_password_hash(raw_password, length=12)

	@classmethod
	def get_by_auth_token(cls, user_id, token, subject='auth'):
		"""Returns a user object based on a user ID and token.

		:param user_id:
		The user_id of the requesting user.
		:param token:
		The token string to be verified.
		:returns:
		A tuple ``(User, timestamp)``, with a user object and
		the token timestamp, or ``(None, None)`` if both were not found.
		"""
		token_key = cls.token_model.get_key(user_id, subject, token)
		user_key = ndb.Key(cls, user_id)
		# Use get_multi() to save a RPC call.
		valid_token, user = ndb.get_multi([token_key, user_key])
		if valid_token and user:
			timestamp = int(time.mktime(valid_token.created.timetuple()))
			return user, timestamp


class qrRef(ndb.Model):
    codeNum = ndb.StringProperty() # unique 4 digit alpha-numeric code
    codeUrl = ndb.StringProperty() # link to tree details associated with QR code
    codeAssigned = ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now=True) # created, then modified date

class treeSpecies(ndb.Model):
    speciesName = ndb.StringProperty()
    commonName = ndb.StringProperty()
    scientificName = ndb.StringProperty()
    ukProvenance = ndb.StringProperty()
    treeType = ndb.StringProperty()
    treeFacts = ndb.TextProperty()
    treeOverview = ndb.TextProperty()
    treeLeaves = ndb.TextProperty()
    treeFlowers = ndb.TextProperty()
    treeFruits = ndb.TextProperty()
    treeMyth = ndb.TextProperty()
    leafPic = ndb.BlobProperty(default=None) # leaf image name
    fruitPic = ndb.BlobProperty(default=None) # fruit image name
    barkPic = ndb.BlobProperty(default=None) # bark image name

class treePlot(ndb.Model):
    username = ndb.StringProperty()
    cDate = ndb.DateTimeProperty(auto_now_add=True) # created date
    mDate = ndb.DateTimeProperty(auto_now=True) # created, then modified date
    treeSpecies = ndb.StringProperty()
    treeDescription = ndb.StringProperty()
    geoLat = ndb.FloatProperty() # Geo Lat
    geoLng = ndb.FloatProperty() # Geo Lng
    qrTagged = ndb.BooleanProperty()
    treeCondition = ndb.StringProperty()
    treeCircum = ndb.StringProperty() # centimetres
    treeLocation = ndb.StringProperty() # descriptive location e.g. private garden, park, street



