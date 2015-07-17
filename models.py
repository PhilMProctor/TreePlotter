from google.appengine.ext import ndb
from webapp2_extras import sessions
from webapp2_extras import auth
from webapp2_extras import security



import webapp2_extras.appengine.auth.models

import logging
import os.path
import webapp2
import time

class qrRef(ndb.Model):
	codeNum = ndb.StringProperty() # unique 4 digit alpha-numeric code
	codeUrl = ndb.StringProperty() # link to tree details associated with QR code
	codeAssigned = ndb.BooleanProperty()
	date = ndb.DateTimeProperty(auto_now=True) # created, then modified date

class treeSpecies(ndb.Model):
	speciesName = ndb.StringProperty()
	treeType = ndb.StringProperty()
	treeDesc = ndb.TextProperty()
	leafPic = ndb.StringProperty() # leaf image name
	fruitPic = ndb.StringProperty() # fruit image name

class treePlot(ndb.Model):
	user = ndb.StringProperty()
	cDate = ndb.DateTimeProperty(auto_now_add=True) # created date
	mDate = ndb.DateTimeProperty(auto_now=True) # created, then modified date
	treeSpecies = ndb.StringProperty()
	treeCodeNum = ndb.StringProperty()
	treeGeoLoc = ndb.GeoPtProperty() # lat log ref
	treeLoc = ndb.StringProperty() # descriptive location e.g. private garden, park, street,
	treeHeightM = ndb.IntegerProperty() # Height measured in metres
	treeHeightR = ndb.StringProperty() # Representitve e.g. Bus Stop, House
	treeWidth = ndb.IntegerProperty() # Width measured in centimetres
	treeCondition = ndb.StringProperty(choices = ['Healthy', 'Damaged', 'Dying'])
	treeAge = ndb.StringProperty(choices = ['Sapling', 'Full', 'Mature'])
	treePic = ndb.StringProperty() # link to picture
	treeComment = ndb.TextProperty() # Free comment option



