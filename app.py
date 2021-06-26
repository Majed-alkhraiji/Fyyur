#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref, session
from sqlalchemy.sql.schema import Table
from forms import *
from flask_migrate import Migrate, show
from datetime import datetime
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



class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable = False)

    artist = db.relationship("Show")

    def __repr__(self):
        return f'<Venue ID:{self.id}, Venue Name:{self.name}, Venue Gernres: {self.genres}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable = False)

    def __repr__(self):
        return f'<Artist ID:{self.id}, Artist Name:{self.name}, Artist Gernres: {self.genres}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.





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


def past_or_upcoming(show_info, status):

  past_shows = 0
  upcoming_shows= 0

  if status == 'upcoming':
    for show in show_info:
      if show.start_time > datetime.now():
        upcoming_shows+=1
    return upcoming_shows

  elif status == 'past':
    for show in show_info:
      if show.start_time > datetime.now():
        past_shows+=1
    return past_shows

  else: 
    for show in show_info:
      if show.start_time < datetime.now():
        past_shows.append({
          "artist_id": show.atrist_id,
          "artist_name": show.artist_name,
          "artist_image_link": show.artist_image_link,
          'start_time': show.start_time
        })
      else:
        upcoming_shows.append({
          "artist_id": show.atrist_id,
          "artist_name": show.artist_name,
          "artist_image_link": show.artist_image_link,
          'start_time': show.start_time
        })

    return past_shows, upcoming_shows
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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.join(Show, Show.venue_id == Venue.id).all()
  
  
  data = []

  for venue in venues:
    data.append({
    'city': venue.city,
    'state': venue.state,
    'id': venue.id,
    'name': venue.name,
    'upcoming_shows': past_or_upcoming(venue.start_time, 'upcoming')
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  key = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(key)).all()
  venue_shows = Venue.query.join(Show, venues.id == Show.venue_id).all()
  data = []

  for venue in venues:
    data.append({
      'id':venue.id,
      'name': venue.name,
      'upcoming_shows': past_or_upcoming(venue_shows, 'upcoming')
    })

  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter(venue_id==Venue.id).first()
  
  
  past_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).join(Artist, Artist.id == Show.artist_id).add_columns(Artist.id, Artist.name , Artist.image_link, Show.start_time).all()
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).join(Artist, Artist.id == Show.artist_id).add_columns(Artist.id, Artist.name , Artist.image_link, Show.start_time).all()


  past_shows_data = []
  upcoming_shows_data =[]

  for show in past_shows:
    past_shows_data.append({
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": show[3]
    })

  for show in upcoming_shows:
    upcoming_shows_data.append({
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": show[3]
    })  

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.addres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }


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

  seeking_talent = False
  if request.form.get('seeking_talent') != None:
    seeking_talent = True

  venue = Venue(name = request.form.get('name'), genres = request.form.get('genres'), city = request.form.get('city'),
                state = request.form.get('state'), address =request.form.get('address'), phone = request.form.get('phone'), website = request.form.get('website'),
                image_link= request.form.get('image_link'), facebook_link=request.form.get('facebook_link'), seeking_description = request.form.get('seeking_description'),
                seeking_talent = seeking_talent)

  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    flash('Venue ' + request.form['name'] + ' couldnt be added. Please try again')
    print(e)
    print('\n \n \n -------------------------------------------------')
    print(request.form.get('seeking_talent'))
    db.session.rollback()
  finally:
    db.session.close()


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue = Venue.query.filter(Venue.id==venue_id)
  db.session.delete(venue)

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  result = Artist.query.all()
 
  return render_template('pages/artists.html', artists=result)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  key = request.form.get('search_term', '')
  result = Artist.query.filter(Artist.name.ilike(key)).all()
  data = []
  
  for artist in result:
      shows = Show.query.join(Artist ,artist.id == Show.artist_id).all()
      data.append({
      'id':artist.id,
      'name': artist.name,
      'num_upcoming_shows': past_or_upcoming(shows, 'upcoming')
    })

  response={
    "count": len(result),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  show_info = Artist.query.join(Show, Show.artist_id==artist_id).all()

  past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).join(Artist, Artist.id == Show.artist_id).add_columns(Artist.id, Artist.name , Artist.image_link, Show.start_time).all()
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).join(Artist, Artist.id == Show.artist_id).add_columns(Artist.id, Artist.name , Artist.image_link, Show.start_time).all()


  past_shows_data = []
  upcoming_shows_data =[]

  for show in past_shows:
    past_shows_data.append({
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": show[3]
    })

  for show in upcoming_shows:
    upcoming_shows_data.append({
      "artist_id": show[0],
      "artist_name": show[1],
      "artist_image_link": show[2],
      "start_time": show[3]
    })  

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id==artist_id).first()
  result={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=result)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter(Venue.id == venue_id).first()
  result={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_venue": venue.seeking_venue,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=result)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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



  seeking_venue = False
  if request.form.get('seeking_venue') != None:
    seeking_venue = True

  artist = Artist(name = request.form.get('name'), genres = request.form.get('genres'), city = request.form.get('city'),
                state = request.form.get('state'), phone = request.form.get('phone'), website = request.form.get('website'),
                image_link= request.form.get('image_link'), facebook_link=request.form.get('facebook_link'), seeking_description = request.form.get('seeking_description'),
                seeking_venue = seeking_venue)

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    flash('Artist ' + request.form['name'] + ' couldnt be added. Please try again')
    db.session.rollback()
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  result = Show.query.join(Venue, Show.venue_id == Venue.id).join(Artist, Show.artist_id == Artist.id).all()

  data = []

  for show in result:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })

  
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
    show = Show(artist_id = request.form.get('artist_id'), venue_id = request.form.get('venue_id'), start_time = request.form.get('start_time'))
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except Exception as e:
    db.session.rollback()
    print(e)
    flash('Something went wrong, Please try again')

  finally:
    db.session.close()

  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flaclass got an unexpected keyword argument sqlalchemy flask when inserting a record.html'), 404

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
