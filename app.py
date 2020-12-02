#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
import sys
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

#Venue Model i put city and state cloumn in  model another  called address 
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    address_id = db.Column(db.Integer,db.ForeignKey('address.id'),nullable =False,)
    shows = db.relationship('Show',backref='venue_show',lazy = True , cascade='all,delete-orphan')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    address_id = db.Column(db.Integer,db.ForeignKey('address.id'),nullable =False)
    shows = db.relationship('Show',backref='artist_show',lazy = True)

class Address(db.Model):
      __tablename__='address'
      id = db.Column(db.Integer,primary_key=True)
      city = db.Column(db.String(),nullable= False)
      state = db.Column(db.String(),nullable = False)
      artists = db.relationship('Artist',backref='address_info_a',lazy = True)
      venues = db.relationship('Venue', backref='address_info_v' ,lazy = True)
#show model have column set start time of the show and
#  type to  set type after get data from database  
class Show(db.Model):
      __tablename__='show'
      id = db.Column(db.Integer,primary_key = True)
      start_time =db.Column(db.DateTime(),nullable = False)
      type = db.Column(db.String(), nullable =True)
      artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable =False)
      venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id',ondelete='CASCADE'),nullable =False)
      
      


   

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


@app.template_filter('strftime')
def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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
  # Get All Venues From Database
  data1 =Address.query.all()

#render  Venues.html 
  return render_template('pages/venues.html', areas=data1);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # get the value of the field of search
  name =request.form['search_term']
  #get the result of search  and put result in response1 which will be list of Venues
  response1 = Venue.query.filter(Venue.name.ilike('%'+name+'%')) 
  #return the number  of  Venue  objects that match pattern of search 
  count =Venue.query.filter(Venue.name.ilike('%'+name+'%')).count()
  #render view of search_venues.html
  return render_template('pages/search_venues.html', 
  results=response1,count=count , search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  #get object Venue that has id = venue_id
  vu =Venue.query.get(venue_id)
  #get genres in list after saving them in database as strings separated by comma
  genres= vu.genres.split(',')
  #get datetime of now in variable  now
  now = datetime.datetime.now()
  #iterate all shows of Venue  and comparing start_time  
  # in shows  with now todetermine type upcoming or past
  for sh in  vu.shows:
       
        if now < sh.start_time :
              sh.type = 'upcoming'
        else :
          sh.type = 'past'    
  #render view of show_venue.html
  return render_template('pages/show_venue.html', venue=vu ,genres= genres)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  #get instance Venue_Form
  form = VenueForm()
  #render view of new_venue.html
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  #intialize error with False  boolean type
  error = False
  try:

    #get data of Venue  from Form of  creation venue
    generies = request.form.getlist('genres')
    genstr = ",".join(map(str,generies))
    state = request.form['state']
    city = request.form['city']
    address = request.form['address']
    name = request.form['name']
    phone = request.form['phone']
    face_link = request.form['facebook_link'] 
    img_link = request.form['image_link']  #"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReZvvWD7eGf-lXe7TVk5jUUrFPTwUrENgtXA&usqp=CAU"
    # get instance of model venue and intialize propertise of new object 
    venue = Venue(genres= genstr ,name =name ,address =address ,phone=phone ,facebook_link =face_link
    ,image_link=img_link )
    
    # check if city and state  are already found in database  or will add them  in table address
    addquer = Address.query.filter_by(city=city).filter_by(state=state).count()
    # get instance of model address and intialize propertise of new object 
    address1 =  Address(city =city,state=state)
    if addquer > 0:
          #found city and state in database 
          address1 = Address.query.filter_by(city=city).filter_by(state=state).first()
          #give id of address object  to  foreignkey field of address_id  in venue
          venue.address_id = address1.id
          db.session.add(venue)
          db.session.commit()
    else:
          #not found city and state  in database add them 
          venue.address_info_v = address1 
          db.session.add(address1)
          db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
        db.session.close()
  if error:
        abort(500)
  else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
  

@app.route('/venues/delete/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
      #delete object of venue with id equal to venue_id from database
      Venue.query.filter_by(id = venue_id).delete()
      db.session.commit()
      flash('Venue Deleted Successfully ')
      #render view of home.html 
      return render_template('pages/home.html')

 
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # get all Artists objects from database
  data1 = Artist.query.all()
  #render view of artist.html
  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
 #get the value of the search field
  name =request.form['search_term']
  #get artist objects that name match the searched pattern  
  response1 = Artist.query.filter(Artist.name.ilike('%'+name+'%')) 
  #get the number of the  objects of artist that match  searched pattern  
  count =Artist.query.filter(Artist.name.ilike('%'+name+'%')).count()
  return render_template('pages/search_artists.html', results=response1,count=count, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
 # get specified artist  from database which id equal to artist_id 
  ar = Artist.query.get(artist_id)
  # get a list of  geners which is  in the list form 
  genres= ar.genres.split(',')
 
  #determine type of show  upcoming or past
  now = datetime.datetime.now()
  for sh in  ar.shows:
       
        if now < sh.start_time :
              sh.type = 'upcoming'
        else :
          sh.type = 'past'      
  return render_template('pages/show_artist.html', artist=ar,genres=genres )

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #get artist with specified id 
  artist = Artist.query.get(artist_id)
 

  return render_template('forms/edit_artist.html', form=form, artist=artist )

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
      #intialize error variable with False 
      error = False
      try :
        #update  artist with new values 
        artist = Artist.query.get(artist_id)
        generies = request.form.getlist('genres')
        artist.genres = ",".join(map(str,generies))
        artist.name = request.form['name']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link'] 
        artist.image_link = request.form['image_link']
        state = request.form['state']
        city = request.form['city']
        #check if artist modified his city  and his state 
        if  artist.address_info_a.city == city and artist.address_info_a.state == state :
              db.session.commit() 
        else:
              #check if new city and state are already  find in database
              addquer = Address.query.filter_by(city=city).filter_by(state=state).count()
              if addquer > 0 :
                    address1 = Address.query.filter_by(city=city).filter_by(state=state).first()
                    artist.address_id = address1.id
                    db.session.commit()
              else :
                    address1 =  Address(city =city,state=state)
                    db.session.add(address1)
                    artist.address_info_a =address1
                    db.session.commit()
      except:
        #set error  with True
        error = True 
        db.session.rollback()
      finally:
        db.session.close()
      if error :
            form = ArtistForm()
            artist = Artist.query.get(artist_id)
            flash('Error ' + artist.name + ' was unsuccessfully updated!')
            return render_template('forms/edit_artist.html', form=form, artist=artist )
      else:
            flash('Artist ' + artist.name + ' successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist.id))
            
                   
  

                  
             
                  
            
    
    

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #get instance of VenueForm 
  form = VenueForm()
  #get specifed venue 
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
      error = False
      try :
        #get values whcich  was entred by user  from Form
        venue = Venue.query.get(venue_id)
        generies = request.form.getlist('genres')
        venue.genres = ",".join(map(str,generies))
        venue.name = request.form['name']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.facebook_link = request.form['facebook_link'] 
        venue.image_link = request.form['image_link']
        state = request.form['state']
        city = request.form['city']
        #check if user  changed city and state or not and if user  
        #  modified them  in the database we will change them 
        if  venue.address_info_v.city == city and venue.address_info_v.state == state :
              db.session.commit() 
        else:
              addquer = venue.query.filter_by(city=city).filter_by(state=state).count()
              if addquer > 0 :
                    address1 = Address.query.filter_by(city=city).filter_by(state=state).first()
                    venue.address_id = address1.id
                    db.session.commit()
              else :
                    address1 =  Address(city =city,state=state)
                    db.session.add(address1)
                    venue.address_info_a =address1
                    db.session.commit()
      except:
        error = True 
        db.session.rollback()
      finally:
        db.session.close()
      if error :
            form = ArtistForm()
            artist = Artist.query.get(artist_id)
            flash('Error ' + venue.name + ' was unsuccessfully updated!')
            return render_template('forms/edit_venue.html', form=form, venue=venue )
      else:
            flash('Venue ' + venue.name + ' successfully updated!')
            return redirect(url_for('show_venue', venue_id=venue.id))
      
      

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = Artist_Form_new()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
      #intialize  error with False Value
      error = False
      try:
        #get value of propertise of artist from form 
        generies = request.form.getlist('genres')
        genstr = ",".join(map(str,generies))
        state = request.form['state']
        city = request.form['city']
        name = request.form['name']
        phone = request.form['phone']
        face_link = request.form['facebook_link'] 
        img_link = request.form['image_link'] #"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReZvvWD7eGf-lXe7TVk5jUUrFPTwUrENgtXA&usqp=CAU"
        artist = Artist(genres= genstr ,name =name  ,phone=phone ,facebook_link =face_link
        ,image_link=img_link )
        #check if city and state are already find in  the database
        addquer = Address.query.filter_by(city=city).filter_by(state=state).count()
        address1 =  Address(city =city,state=state)
        if addquer > 0:
              address1 = Address.query.filter_by(city=city).filter_by(state=state).first()
              artist.address_id = address1.id 
              db.session.add(artist)
              db.session.commit()
        else:
              #if they not found in the database we will put them in the database
              artist.address_info_a = address1 
              db.session.add(address1)
              db.session.commit()
      except:
        db.session.rollback()
        error = True
      finally:
        db.session.close()
      if error:
            flash('An error occurred. Artist ' + artist.name+ ' could not be listed.')
            return render_template('pages/home.html')
            
      else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 #get all shows from database 
  shows =Show.query.all()
  #determination  shows of upcoming type
  now = datetime.datetime.now()
  for sh in  shows:
       
        if now < sh.start_time :
              sh.type = 'upcoming'
        else :
              sh.type = 'past'    
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm() #show_form_new() we can use this for if we do name uniqu field in db 
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
      #intialize error wit False
      error = False 
      try:
        #get value from Form of show
        artist_id= request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        artist = Artist.query.get(artist_id)
        venue = Venue.query.get(venue_id)
        #verify that  artist and venue found
        if artist != None  and venue !=  None :
              #add new show 
              show = Show(start_time=start_time)
              show.artist_show = artist
              show.venue_show = venue
              db.session.add(artist)
              db.session.commit()
              flash('Show was successfully listed!')
        else:
             flash('error id of artist or venue not true.','error')
             return redirect(url_for('create_shows'))
      except:
        db.session.rollback()
        error = True
      finally:
        db.session.close()  
      if error:
            flash('An error occurred. Show could not be listed.','error')
            return render_template('pages/home.html')
      else:
            return render_template('pages/home.html')    
    

@app.route('/show/search', methods=['POST'])
def search_show():
      #searching for show with artist name or venue name
      
      name =request.form['search_term']
      response1 = Artist.query.filter(Artist.name.ilike('%'+name+'%')).first()
      if response1 == None :
            response1 = Venue.query.filter(Venue.name.ilike('%'+name+'%')).first() 
      return render_template('pages/show.html',
       result=response1.shows, search_term=request.form.get('search_term', ''))

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
