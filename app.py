#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
#db.create_all()

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


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
  #num_shows should be aggregated based on number of upcoming shows per venue.
    areas = db.session.query(Venue.city, Venue.state).distinct()
    data = []

    for venue in areas:
        venue = dict(zip(('city', 'state'), venue))
        venue['venues'] = []
        for venue_data in Venue.query.filter_by(
            city=venue['city'],
            state=venue['state']
        ).all():
            shows = Show.query.filter_by(
                venue_id=venue_data.id
            ).all()
            venues_data = {
                'id': venue_data.id,
                'name': venue_data.name,
                'num_upcoming_shows': len(shows)
            }
            venue['venues'].append(venues_data)
        data.append(venue)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', None)

    venues = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()

    count_venues = len(venues)

    response = {
        'cout': count_venues,
        'data': venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
    venue = Venue.query.filter_by(id=venue_id).first()

    # upcoming_shows = [
    # show for show in Show.query.filter(
    # Show.start_time > datetime.datetime.now(),
    # Show.venue_id == Show.id).all()
    # ]
    # past_shows = [
    # show for show in Show.query.filter(
    # Show.start_time < datetime.datetime.now(), Show.venue_id == Show.id
    # ).all()
    # ]

  # TODO: replace with real venue data from the venues table, using venue_id
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': [venue.genres],
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website': venue.website,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        # 'upcoming_shows': upcoming_shows,
        # 'past_shows': past_shows,
        # 'upcoming_shows_count': len(upcoming_shows),
        # 'past_shows_count': len(past_shows),

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
    try:
        seeking_talent = False
        seeking_description = ''
        if 'seeking_talent' in request.form:
            seeking_talent = request.form['seeking_talent'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        if 'seeking_description' not in request.form == '':
            seeking_description = 'We are looking for talents!'

        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form['genres'],
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )

        db.session.add(new_venue)
        db.session.commit()
  # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        error = True
        db.session.rollback()
        flash(
            'An error occurred. Venue '
            + request.form['name']
            + ' could not be listed.'
        )
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    try:
        venue = Venue.query.filter_by(id=venue_id).first_or_404()
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.filter_by(id=artist_id).first_or_404()
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', None)

    artists = Artist.query.filter(
        Artist.name.ilike(
            '%{}%'.format(search_term)
        )
    )

    if artists:
        count_artists = func.len(artists)

        response = {'cout': count_artists, 'data': artists}

        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)

    # upcoming_shows = [
    # show for show in Show.query.filter(
    #   Show.start_time > datetime.datetime.now(),
    #   Show.artist_id == Show.artist_id).all()]
    # past_shows = [
    #   show for show in Show.query.filter(
    #   Show.start_time < datetime.datetime.now(),
    #   Show.artist_id == Show.id).all()
    # ]

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': [artist.genres],
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'seeking_venue': True,
        'image_link': artist.image_link,
        'facebook_link': artist.facebook_link,
        'website': artist.website,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        # 'upcoming_shows': upcoming_shows,
        # 'past_shows': past_shows,
        # 'upcoming_shows_count': len(upcoming_shows),
        # 'past_shows_count': len(past_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)

  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get(artist_id)
        form = ArtistForm()

        seeking_venue = False
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'

            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.phone = request.form['phone']
            artist.website = request.form['website']
            artist.image_link = request.form['image_link']
            artist.genres = request.form['genres']
            artist.facebook_link = request.form['facebook_link']
            artist.seeking_venue = seeking_venue
            artist.seeking_description = request.form['seeking_description']

        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully edited!')

    except:
        db.session.rollback()
        flash(
            'An error occurred. Artist '
            + request.form['name']
            + ' could not be edited.'
        )

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)

  # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
    try:
        venue = Venue.query.get(venue_id)
        form = VenueForm()
        seeking_talent = False

        if 'seeking_talent' in request.form:
            seeking_talent = request.form['seeking_talent'] == 'y'

            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.phone = request.form['phone']
            venue.website = request.form['website']
            venue.image_link = request.form['image_link']
            venue.genres = request.form['genres']
            venue.facebook_link = request.form['facebook_link']
            venue.seeking_talent = seeking_talent
            venue.seeking_description = request.form['seeking_description']

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')

    except:
        db.session.rollback()
        flash(
            'An error occurred. Artist '
            + request.form['name']
            + ' could not be edited.'
        )
    finally:
        db.session.close()

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
    try:
        seeking_venue = False
        seeking_description = ''
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        if 'seeking_description' not in request.form == '':
            seeking_description = 'We are looking for venues!'

        new_artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            genres=request.form['genres'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )

        db.session.add(new_artist)
        db.session.commit()

  # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    except:
        db.session.rollback()
        flash(
            'An error occurred. Artist '
            + request.form['name']
            + ' could not be listed.'
        )

    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = Show.query.all()
    data = []

    for show in shows:
        show = {
            'venue_id': show.venue_id,
            'venue_name': db.session.query(
                Venue.name
            ).filter_by(
                id=show.venue_id
            ).first()[0],
            'artist_id': show.artist_id,
            'artist_name': db.session.query(
                Artist.name
            ).filter_by(
                id=show.artist_id
            ).first()[0],
            'artist_image_link': db.session.query(
                Artist.image_link
            ).filter_by(
                id=show.artist_id
            ).first()[0],
            'start_time': str(show.start_time)
        }
        data.append(show)

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
    error = False
    try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()

  # on successful db insert, flash success
        flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
