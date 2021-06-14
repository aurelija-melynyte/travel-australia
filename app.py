import os
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import random
from data import location_list
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
import forms
from constants.password import slaptazodis, gmail_password, api_key_pixabay, map_key
import psycopg2
from geopy.geocoders import Nominatim
import smtplib
from email.message import EmailMessage
from scraping import temp_dict

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:'+slaptazodis+'@localhost/a_new_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.Login_message_category = 'info'
login_manager.login_message = 'You have to login to access all features'


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(40), unique=True, nullable=False)
    surname = db.Column('surname', db.String(40), unique=True, nullable=False)
    email = db.Column('email', db.String(150), unique=True, nullable=False)
    password = db.Column('password', db.String(80), unique=True, nullable=False)


class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    territory = db.Column('territory', db.String(40), nullable=False)
    placetogo = db.Column('placetogo', db.String(150),  nullable=False)
    description = db.Column('description', db.String(3000), nullable=False)


email = EmailMessage()
email['from'] = 'travel-australia'
email['to'] = 'aurelijamelynyte@gmail.com'
email['subject'] = 'new user registration'

your_location_list = []

@login_manager.user_loader
def load_user(user_id):
    db.create_all()
    return User.query.get(int(user_id))


@app.route('/registration', methods=['GET', 'POST'])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        enc_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, surname=form.surname.data, email=form.email.data, password=enc_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration was successful', 'success')

        """laisko siuntimas"""
        email.set_content('Hello,\n\nNew user '+user.name+' '+user.surname+
                          ' has been registered\n\nBest regards,\n\ntravel-australia')
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login('aurelijamelynyte@gmail.com', gmail_password)
            smtp.send_message(email)

        return redirect(url_for('index'))

    return render_template('registration.html', title='Registration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.rememberme.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login was not successful. Please check your password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cities')
def cities():
    return render_template('cities.html', temp_dict=temp_dict)


@app.route('/placestovisit', methods=['GET', 'POST'])
def placestovisit():

    """paveiksliuku uzkrovimas"""
    def open_first(query):
        payload = {'key': api_key_pixabay, 'q': query, 'img_type': 'photo', 'per_page': 100, 'pretty': 'true'}
        r = requests.get('http://pixabay.com/api/', params=payload)
        json_str = r.text
        result = json.loads(json_str)
        img_list = []
        for i in range(300):
            sk = random.randint(0, 40)
            image = result['hits'][sk]['largeImageURL']
            img_list.append(image)
        return img_list

    """pridedama lokacija jeigu tokia dar neegzistuoja is pagrindines db i nauja db(pasalinti duomenu pasikartojimus)"""
    db.create_all()
    for data in location_list:
        (a, b, c) = data
        location = Location(territory=a, placetogo=b, description=c)
        loc = Location.query.filter_by(placetogo=b).first()
        if not loc:
            db.session.add(location)
            db.session.commit()

    conn = psycopg2.connect(host='localhost', database="a_new_database", user="postgres", password=slaptazodis)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""Select * from public.locations""")
    new_locations = cur.fetchall()

    """ikeliamos visos buvusios ir pridetos lokacijos"""
    new_locations_list = []
    for el in new_locations:
        el_tuple = (el[1], el[2], el[3])
        new_locations_list.append(el_tuple)

    """Norimo lokaciju saraso sudarymas"""
    if request.method == "POST":
        add_to_list = request.form.get("add_your_location")
        if add_to_list in your_location_list:
            flash("Location already added to your list!",'danger')
        else:
            your_location_list.append(add_to_list)
            print(your_location_list)
            flash("Location added to your list!",'success')
        remove_from_list = request.form.get('remove_your_location')
        if remove_from_list in your_location_list:
            your_location_list.remove(remove_from_list)

    return render_template('placestovisit.html', image=open_first('australia'), values=new_locations_list,
                           list=your_location_list)


@app.route('/addlocation', methods=['GET', 'POST'])
def newlocation():
    db.create_all()
    form = forms.AddForm()
    if form.validate_on_submit():
        add_location = Location(territory=form.territory.data, placetogo=form.placetogo.data, description=form.description.data)
        old_loc = Location.query.filter_by(placetogo=form.placetogo.data).first()
        if not old_loc:
            db.session.add(add_location)
            db.session.commit()
            flash('Location was added successfully', 'success')
        else:
            flash('Location already exists', 'danger')
        return redirect(url_for('placestovisit'))
    return render_template('addlocation.html', title='AddLocation', form=form)


@app.route('/map')
def mapview():
    geolocator = Nominatim(user_agent="travel-australia")
    coordinates = []
    for i in your_location_list:
        location = geolocator.geocode(i)
        coordinates_list = [location.latitude, location.longitude]
        coordinates.append(coordinates_list)
    list_length = len(coordinates)
    return render_template('map.html', coordinates=coordinates, list_length=list_length, map_key=map_key)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8015, debug=True)
    db.create_all()