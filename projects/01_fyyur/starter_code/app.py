#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
import sys
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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  data = []

  try:
    countries = db.session.query(Venue).distinct(Venue.city, Venue.state).all()

    for country in countries:
       venues = db.session.query(Venue).filter_by(city=country.city,
                                                       name=country.name)
       venue_list=[]
       for venue in venues:
          print("id:%s,name:%s"%(venue.id, venue.name))
          venue_struct={"id": venue.id,
                      "name": venue.name,
                      "num_upcoming_shows": 0}
          venue_list.append(venue_struct)

       dataElmnt = {"city": country.city, 
                    "state": country.state,
                    "venues": venue_list}
       data.append(dataElmnt)

  except:
    db.session.close()
    print(sys.exc_info)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  try: 
     # Find venues suiting to search term
     search_term = request.form.get('search_term')
     listOfVenues = db.session.query(Venue).filter(Venue.name.ilike('%'+search_term+'%'))        
     # Determine amount of suitable venues
     ListOfVenues_Count = listOfVenues.count()

     data = []
     for ven in listOfVenues:       
       # determine amount of upcoming shows
       amount_of_upcoming_shows = db.session.query(Show).filter(Show.venue_id==ven.id).count()

       elemnt = {'id': ven.id,
                'name': ven.name,
                'num_upcoming_shows': amount_of_upcoming_shows}
       data.append(elemnt)

       response={
        "count": ListOfVenues_Count,
        "data": data
       }
  except:
    db.session.close()
    print(sys.exc_info)
    response={
      "count": 0,
      "data": []
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data={"id": 0,
        "name": "",
        "genres": [],
        "address": "",
        "city": "",
        "state": "",
        "phone": "",
        "website_link": "",
        "facebook_link": "",
        "seeking_talent": False,
        "seeking_description": "",
        "image_link": "",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0}
  
  try:
     venue = Venue.query.get(venue_id)
     data["id"] = venue.id
     data["name"] = venue.name
     genre_assignments=db.session.query(GenreAssignment).filter(
          GenreAssignment.venue_id==venue_id)
     genres=[]
     for genre_assignment in genre_assignments:
        genres.append(genre_assignment.genre)
     data["genres"] = genres
     data["address"] = venue.address
     data["city"] = venue.city
     data["state"] = venue.state
     data["phone"] = venue.phone
     data["website_link"] = venue.website_link
     data["facebook_link"] = venue.facebook_link
     data["seeking_talent"] = venue.seeking_talent
     data["seeking_description"] = venue.seeking_description     
     data["image_link"] = venue.image_link

     # date time data for past shows
     past_shows = db.session.query(Show).filter(
        (Show.venue_id==venue.id)).filter(
          (Show.start_time<datetime.now()))
     past_shows_array=[]
     for show in past_shows:
        elmnt={
          "artist_image_link":Artist.query.get(show.artist_id).image_link,
          "artist_id":show.artist_id,
          "artist_name":Artist.query.get(show.artist_id).name,
          "start_time":format_datetime(
              show.start_time.strftime("%y-%m-%d %H:%M:%S"))}
        past_shows_array.append(elmnt)
     data["past_shows"] = past_shows_array
     data["past_shows_count"] = past_shows.count()

     # date time data for upcoming shows
     upcoming_shows = db.session.query(Show).filter(
        (Show.venue_id==venue.id)).filter(
          (Show.start_time>datetime.now()))
     upcoming_shows_array=[]
     for show in upcoming_shows:
        elmnt={
          "artist_image_link":Artist.query.get(show.artist_id).image_link,
          "artist_id":show.artist_id,
          "artist_name":Artist.query.get(show.artist_id).name,
          "start_time":format_datetime(
              show.start_time.strftime("%y-%m-%d %H:%M:%S"))}
        upcoming_shows_array.append(elmnt)
     data["upcoming_shows"] = upcoming_shows_array
     data["upcoming_shows_count"] = upcoming_shows.count()

  except:
    db.session.close()
    print(sys.exc_info)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # Introducing flag to validate, if new venue post succeeded
  venue_post_succeeded=True

  # init data buffer
  data={
      'name': '', 
      'city': '', 
      'state': '',
      'address': '',
      'phone': '',
      'image_link': '',
      'facebook_link': '',
      'seeking_talent': False,
      'website_link': '',
      'seeking_description': ''}

  try: 
    data['name']=request.form.get('name')
    data['city']=request.form.get('city')
    data['state']=request.form.get('state')
    data['address']=request.form.get('address')
    data['phone']=request.form.get('phone')
    data['image_link']=request.form.get('image_link')
    data['facebook_link']=request.form.get('facebook_link')
    data['seeking_talent']=False
    data['website']=request.form.get('website_link')
    data['seeking_description']=request.form.get('seeking_description')

    if request.form.get('seeking_talent')=='y':
      data['seeking_talent']=True
    else:
      data['seeking_talent']=False

    venue = Venue(name=data['name'],
                  city=data['city'],
                  state=data['state'],
                  address=data['address'],
                  phone=data['phone'],
                  image_link=data['image_link'],
                  facebook_link=data['facebook_link'],
                  seeking_talent=data['seeking_talent'],
                  website_link=data['website_link'],
                  seeking_description=data['seeking_description'])
     
    db.session.add(venue)
    db.session.commit()

  except:
     db.session.rollback()
     print(sys.exc_info())
     venue_post_succeeded=False
  
  finally:
     db.session.close()

  # on successful db insert, flash success
  if venue_post_succeeded:
    flash('Venue ' + data['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
     db.session.rollback()
     print(sys.exc_info())
     print('Deletion of item %s failed.' % venue_id)
  finally:
     db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  
  data=[]
  for artist in artists:
     element={"id":artist.id,"name":artist.name}
     data.append(element)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  try:
    search_term = request.form.get('search_term')
    listOfArtists = db.session.query(Artist).filter(
       Artist.name.ilike('%'+search_term+'%'))
    # Determine amount of suitable artists
    listOfArtists_Count = listOfArtists.count()
    
    data = []
    for artist in listOfArtists:
      # determine amount of upcoming shows
      amount_of_upcoming = db.session.query(Artist).filter(
          (Show.artist_id==artist.id)).filter( 
            (Show.start_time>datetime.now())).count()
      
      elmnt = {
          'id': artist.id,
          'name': artist.name,
          'num_upcoming_shows': amount_of_upcoming
      }
      data.append(elmnt)

    response={
      "count": listOfArtists_Count,
      "data": data
    }
  except:
    db.session.close()
    print(sys.exc_info)
    response={
      "count": 0,
      "data": []
    }
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  data={
    "id": "",
    "name": "",
    "genres": [],
    "city": "",
    "state": "",
    "phone": "",
    "website_link": "",
    "facebook_link": "",
    "seeking_venue": "",
    "seeking_description": "",
    "image_link": "",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0}

  try:
    artist = Artist.query.get(artist_id)
    
    data["id"]=artist.id
    data["name"]=artist.name
    genre_assignments=db.session.query(GenreAssignment).filter(
      GenreAssignment.artist_id==artist_id)
    genres=[]
    for genre_assignment in genre_assignments:
      genres.append(genre_assignment.genre)
    data["genres"] = genres
    data["city"]=artist.city
    data["state"]=artist.state
    data["phone"]=artist.phone
    data["website_link"]=artist.website_link
    data["facebook_link"]=artist.facebook_link
    data["seeking_venue"]=artist.seeking_venue
    data["seeking_description"]=artist.seeking_description
    data["image_link"]=artist.image_link

    # date time data for past shows
    past_shows = db.session.query(Show).filter(
      (Show.venue_id==artist.id)).filter(
       (Show.start_time<datetime.now()))
    past_shows_array=[]
    for show in past_shows:
      elmnt={
        "venue_image_link":Venue.query.get(show.venue_id).image_link,
        "venue_id":show.venue_id,
        "venue_name":Venue.query.get(show.venue_id).name,
        "start_time":format_datetime(
            show.start_time.strftime("%y-%m-%d %H:%M:%S"))}
      past_shows_array.append(elmnt)
    data["past_shows"] = past_shows_array
    data["past_shows_count"] = past_shows.count()

    # date time data for upcoming shows
    upcoming_shows = db.session.query(Show).filter(
      (Show.artist_id==artist.id)).filter(
       (Show.start_time>datetime.now()))
    upcoming_shows_array=[]
    for show in upcoming_shows:
      elmnt={
        "venue_image_link":Venue.query.get(show.venue_id).image_link,
        "venue_id":show.venue_id,
        "venue_name":Venue.query.get(show.venue_id).name,
        "start_time":format_datetime(
          show.start_time.strftime("%y-%m-%d %H:%M:%S"))}
      upcoming_shows_array.append(elmnt)
    data["upcoming_shows"] = upcoming_shows_array
    data["upcoming_shows_count"] = upcoming_shows.count()

  except:
     db.session.close()
     print(sys.exc_info)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist={
    "id":artist_id,
    "name":Artist.query.get(artist_id).name
  }  

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    if request.form.get('seeking_talent')=='y':
      seeking_venue=True
    else:
      seeking_venue=False

    artist=Artist.query.get(artist_id)
    artist.name=request.form.get('name')
    artist.city=request.form.get('city')
    artist.state=request.form.get('state')
    artist.phone=request.form.get('phone')
    artist.image_link=request.form.get('image_link')
    artist.facebook_link=request.form.get('facebook_link')
    artist.website_link=request.form.get('website_link')
    artist.seeking_venue=request.form.get(seeking_venue)
    artist.seeking_description=request.form.get('seeking_description')

    GenreAssignment.query.filter(
      GenreAssignment.artist_id==artist_id).delete()

    for genre in request.form.getlist('genres'):
      genre_set = GenreAssignment(artist=artist, genre=Genre(genre))
      db.session.add(genre_set)

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
     db.session.rollback()
     print(sys.exc_info)
     flash('Artist ' + request.form['name'] + ' was not successfully listed!')
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue=Venue.query.get(venue_id)

  data={
    "id": venue_id,
    "name": venue.name,
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try:
    if request.form.get('seeking_talent')=='y':
      seeking_venue=True
    else:
      seeking_venue=False

    venue=Venue.query.get(venue_id)
    venue.name=request.form.get('name')
    venue.city=request.form.get('city')
    venue.state=request.form.get('state')
    venue.phone=request.form.get('phone')
    venue.image_link=request.form.get('image_link')
    venue.facebook_link=request.form.get('facebook_link')
    venue.website_link=request.form.get('website_link')
    venue.seeking_venue=request.form.get(seeking_venue)
    venue.seeking_description=request.form.get('seeking_description')

    GenreAssignment.query.filter(
      GenreAssignment.venue_id==venue_id).delete()
    
    for genre in request.form.getlist('genres'):
      genre_set = GenreAssignment(venue_id=venue_id, genre=Genre(genre))
      db.session.add(genre_set)

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    print(sys.exc_info)
    flash('Artist ' + request.form['name'] + ' was not successfully listed!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    if request.form.get('seeking_talent')=='y':
      seeking_venue=True
    else:
      seeking_venue=False

    artist=Artist(name=request.form.get('name'),
                  city=request.form.get('city'),
                  state=request.form.get('state'),
                  phone=request.form.get('phone'),
                  image_link=request.form.get('image_link'),
                  facebook_link=request.form.get('facebook_link'),
                  website_link=request.form.get('website_link'),
                  seeking_venue=request.form.get(seeking_venue),
                  seeking_description=request.form.get('seeking_description'))
    
    db.session.add(artist)

    for genre in request.form.getlist('genres'):
      genre_set = GenreAssignment(artist=artist, genre=Genre(genre))
      db.session.add(genre_set)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
     db.session.rollback()
     print(sys.exc_info)
     flash('Artist ' + request.form['name'] + ' was not successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  try:
    shows = Show.query.all()
    data=[]
    for show in shows:
      elment={
          "venue_id":show.id,
          "venue_name":Venue.query.get(show.venue.id).name,
          "artist_id":show.artist_id,
          "artist_name":Artist.query.get(show.artist.id).name,
          "artist_image_link":Artist.query.get(show.artist.id).image_link,
          "start_time":format_datetime(show.start_time.strftime("%y-%m-%d %H:%M:%S"))
      }
      data.append(elment)

  except:
     print(sys.exc_info)
     data=[{
          "venue_id":"test",
          "venue_name":"test",
          "artist_id":"test",
          "artist_name":"test",
          "artist_image_link":"test",
          "start_time":format_datetime(datetime.now().strftime("%y-%m-%d %H:%M:%S"))
     }]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  try:
     show = Show(artist_id=request.form.get('artist_id'),
                 venue_id=request.form.get('venue_id'),
                 start_time=request.form.get('start_time'))
     db.session.add(show)
     db.session.commit()
     # on successful db insert, flash success
     flash('Show was successfully listed!')

  except:
     # TODO: on unsuccessful db insert, flash an error instead.
     # e.g., flash('An error occurred. Show could not be listed.')
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     db.session.rollback()
     print(sys.exc_info)
     flash('Show was not successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
