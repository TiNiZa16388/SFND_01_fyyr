#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from forms import Genre
from flask_migrate import Migrate
from flask_moment import Moment
from flask import Flask

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Model moved from app.py

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_talent = db.Column(db.Boolean(), default=False)
    website_link = db.Column(db.String())
    seeking_description = db.Column(db.String())
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, default=False)
    website_link = db.Column(db.String())
    seeking_description = db.Column(db.String())
    genres = db.relationship('GenreAssignment', backref='artist', lazy=True)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class GenreAssignment(db.Model):
   __tablename__ = 'GenreAssignment'
   
   id = db.Column(db.Integer, primary_key=True)
   genre = db.Column(Enum(Genre))
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
   

class Show(db.Model):
   __tablename__ = 'Show'

   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime)

   artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
   artist = db.relationship('Artist', backref=db.backref('show',lazy=True))
   venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
   venue = db.relationship('Venue', backref=db.backref('show',lazy=True))
   start_time = db.Column(db.DateTime)

