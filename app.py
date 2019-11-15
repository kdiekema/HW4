from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
import secrets
#import os




#dbuser = os.environ.get('DBUSER')
#dbpass = os.environ.get('DBPASS')
#dbhost = os.environ.get('DBHOST')
#dbname = os.environ.get('DBNAME')

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class kdiekema_petsapp(db.Model):
    petID = db.Column(db.Integer, primary_key=True)
    petName = db.Column(db.String(255))
    petType = db.Column(db.String(255))
    age= db.Column(db.Integer)


class PetsForm(FlaskForm):
    petID = IntegerField('Pet ID:')
    petName = StringField('Pet Name:', validators=[DataRequired()])
    petType = StringField('Pet Type:', validators=[DataRequired()])
    age = IntegerField('Pet Age:', validators=[DataRequired()])

@app.route('/')
def index():
    all_pets= kdiekema_petsapp.query.all()
    return render_template('index.html', pets=all_pets, pageTitle="Pets")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = kdiekema_petsapp.query.filter(or_(kdiekema_petsapp.petName.like(search), kdiekema_petsapp.petType.like(search))).all()
        return render_template('index.html', pets=results, pageTitle='Karina\'s Pets')
    else:
        return redirect('/')

@app.route('/add_pet', methods=['GET','POST'])
def add_pet():
    form = PetsForm()
    if form.validate_on_submit():
        pet = kdiekema_petsapp(petName=form.petName.data, petType=form.petType.data, age= form.age.data)
        db.session.add(pet)
        db.session.commit()
        return redirect('/')

    return render_template('add_pet.html', form=form, pageTitle='Add Pet')


@app.route('/pet/<int:petID>', methods=['GET','POST'])
def pet(petID):
    pet = kdiekema_petsapp.query.get_or_404(petID)
    return render_template('pet.html', form=pet, pageTitle='Pet Details')

@app.route('/pet/<int:petID>/update', methods=['GET','POST'])
def update_pet(petID):
    pet = kdiekema_petsapp.query.get_or_404(petID)
    form = PetsForm()
    if form.validate_on_submit():
        pet.petID = form.petID.data
        pet.petName = form.petName.data
        pet.petType = form.petType.data
        pet.age = form.age.data
        db.session.commit()
        flash('Your pet has been updated.')
        return redirect(url_for('pet', petID=pet.petID))
    #elif request.method == 'GET':
    form.petID.data = pet.petID
    form.petName.data = pet.petName
    form.petType.data = pet.petType
    form.age.data = pet.age
    return render_template('update_pet.html', form=form, pageTitle='Update Post',
                            legend="Update A pet")

@app.route('/pet/<int:petID>/delete', methods=['POST'])
def delete_pet(petID):
    if request.method == 'POST': #if it's a POST request, delete the pet from the database
        pet = kdiekema_petsapp.query.get_or_404(petID)
        db.session.delete(pet)
        db.session.commit()
        flash('Pet was successfully deleted!')
        return redirect("/")
    else: #if it's a GET request, send them to the home page
        return redirect("/")


if __name__ == '__main__':
    app.run(debug==True)
