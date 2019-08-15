
import os
from flask import Flask, render_template, url_for, redirect, request, session
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId 

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'tandev'
app.config['MONGO_URI']= os.environ.get("MONGO_URI")
app.secret_key = os.urandom(24)

mongo = PyMongo(app)

client = MongoClient(app.config['MONGO_URI'])
db = client.tandev

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():

# Create a list of 6 random profiles whose display key is set to 'True' to be used in the index.html carousel.


    carousel = db.profile.aggregate( [{ "$match" : { "display" : True } }, { "$sample": { "size": 6 } } ])
    carousel = list(carousel)
    return render_template("pages/index.html", active="index", carousel=carousel)

#About page

@app.route('/about', methods=['GET'])
def about():
    return render_template("pages/about.html", active="about")


#Search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template("pages/search.html", active="search")

@app.route('/logreg', methods=['GET', 'POST'])
def logreg():
    return render_template("pages/logreg.html", active="logreg")



if __name__ == '__main__':
    app.run(host=os.getenv('IP'), port=(os.getenv('PORT')), debug="True")