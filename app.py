from flask import Flask
from flask import render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

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
    petName = StringField('Pet Name:', validators=[DataRequired()])
    petType = StringField('Pet Type:', validators=[DataRequired()])
    age = IntegerField('Pet Age:', validators=[DataRequired()])

@app.route('/')
def index():
    all_pets= kdiekema_petsapp.query.all()
    return render_template('index.html', pets=all_pets, pageTitle="Pets")

@app.route('/add_pet', methods=['GET','POST'])
def add_pet():
    form = PetsForm()
    if form.validate_on_submit():
        pet = kdiekema_petsapp(petName=form.petName.data, petType=form.petType.data, age= form.age.data)
        db.session.add(pet)
        db.session.commit()
        return redirect('/')

    return render_template('add_pet.html', form=form, pageTitle='Add Pet')

@app.route('/delete_pet/<int:petID>', methods=['GET','POST'])
def delete_pet(petID):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        obj = kdiekema_petsapp.query.filter_by(petID=petID).first()
        db.session.delete(obj)
        db.session.commit()
        flash('Pet was successfully deleted!')
        return redirect("/")

    else: #if it's a GET request, send them to the home page
        return redirect("/")


if __name__ == '__main__':
    app.run(debug==True)
