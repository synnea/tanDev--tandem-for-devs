
import os
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import json

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'tandev'
app.config['MONGO_URI']= os.environ.get("MONGO_URI")

# Assign a randomized secret key
app.secret_key = os.urandom(24)

mongo = PyMongo(app)

client = MongoClient(app.config['MONGO_URI'])
db = client.tandev

#Helper Lists
skills = list(["CSS", "JavaScript", "React", "Vue", "Angular",  "UX", "Web Design", "SQL", "Python", "PHP", "Ruby", "C++", "C#",
"Java", "Rust", "Go", "Swift", "Kotlin", "Perl" ])

commstyles = list(["Text", "Video", "In person"])

other = list(["Project Work", "For Hire", "Looking for Co-Founder"])



# Begin creating routes
# Index page
@app.route('/', methods=['GET'])
def index():
    """ Create a list of 6 random profiles whose display key is set to 'True' to be used in the index.html carousel. """

    loggedIn = True if 'username' in session else False


    carousel = db.profile.aggregate( [ { "$match" : { "display" : True } }, { "$sample": { "size": 6 } } ])
    carousel = list(carousel)
    return render_template("pages/index.html", active="index", carousel=carousel, loggedIn=loggedIn)



#About page
@app.route('/about', methods=['GET'])
def about():

    loggedIn = True if 'username' in session else False

    return render_template("pages/about.html", active="about", loggedIn=loggedIn)



# Search page
@app.route('/search', methods=['GET', 'POST'])
def search():

    loggedIn = True if 'username' in session else False

    return render_template("pages/search.html", active="search", loggedIn=loggedIn)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Checks if the user already exists in the database. If they don't exist, the user is notified of this. 
    If the username does exist, the password is matched against it. If it matches, the user is logged in.
    Otherwise, the user is notified that his username and password combination didn't match. """

    loggedIn = True if 'username' in session else False

    if request.method == 'POST' and request.form['btn'] == 'login':
        existing_user = db.profile.find_one({'username': request.form.get('username')})
        if not existing_user:
            flash("Hmm... this username doesn't seem to exist.", "error")
            return redirect(url_for('login'))

        if check_password_hash(existing_user["password"], 
        request.form.get("password")):
            session['username'] = request.form.get('username')
            return redirect(url_for('profile', username = session['username']))
        else:
            flash("Uh-oh! Username and password combo doesn't match.", "error")
            return redirect(url_for('login'))

    else:
        return render_template("pages/logreg.html", active="logreg", loggedIn=loggedIn)


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """ Check if the username already exists in the database. Return warning to the user if it exists.
    If it doesn't exist, add user to the database and create a new document in the database.
    This function was written with the help of Tim Nelson who helped me get the hang of Python backend coding, so I could do
    the remaining functions on my own. """

    loggedIn = True if 'username' in session else False

    if request.method == 'POST' and request.form['btn'] == 'register':
        exists = db.profile.find_one({'username': request.form.get('username')})
        if exists:
            flash("Sorry, this username already exists", "error")
            return redirect(url_for('register', _anchor = 'register-tab'))
        register = {
            "username": request.form.get('username'),
            "email": "",
            "password": generate_password_hash(request.form.get('password')),
            "imgURL": "",
            "district": "",
            "shortDescription": "",
            "description": "",
            "experience": "",
            "communicationStyle": [],
            "skills": [],
            "desiredSkills": [],
            "otherDetails": [],
            "github": "",
            "linkedin": "",
            "twitter": "",
            "registered": datetime.now().strftime("%d-%M-%Y"),
            "published": "",
            "display": False
        }
        db.profile.insert_one(register)
        session['username'] = request.form.get('username')
        return redirect(url_for('newprofile', username = session['username']))

    return render_template("pages/logreg.html", active="logreg", loggedIn=loggedIn)


# New profile
@app.route('/newprofile/<username>', methods = ['GET', 'POST'])
def newprofile(username):
    """ Check if the user selected at least skill and one desired skill.
    If they haven't, display an error message.
    Else, if all requirements are met, add the new data to the user's database document """

    loggedIn = True if 'username' in session else False

    if loggedIn == False:
        return redirect(url_for('forbidden'))


    if request.method == 'POST':
        
        if request.form.getlist("skills") and request.form.getlist("desiredSkills") != "":

            db.profile.update_many( {'username': username},
            { "$set": {
                'shortDescription': request.form.get('shortDescription'),
                "imgURL": request.form.get('imgURL'),
                "district": request.form.get('district'),
                "skills": request.form.getlist("skills"),
                "desiredSkills": request.form.getlist("desiredSkills"),
                "communicationStyle": request.form.getlist("communicationStyle"),
                "otherDetails": request.form.getlist("other"),
                "published": datetime.now().strftime("%d-%M-%Y"),
                "github": request.form.get('github'),
                "linkedin": request.form.get('linkedin'),
                "twitter": request.form.get('twitter')

            }})

            flash("Changes saved successfully. Scroll down to preview or edit.", "success")

            return redirect(url_for('profile', username = session['username']))

        else:
            flash("Please select at least one acquired and one desired skill", "error")
            return redirect(url_for('newprofile', username = session['username'])) 

    return render_template("pages/newprofile.html", username=username, active="profile", loggedIn=loggedIn, skills=skills,
    commstyles=commstyles, other=other)


# Profile page
@app.route('/myprofile/<username>', methods = ['GET', 'POST'])
def profile(username):
    loggedIn = True if 'username' in session else False

    if loggedIn == False:
        return redirect(url_for('forbidden'))

    username = db.profile.find_one({"username": username})

    if request.method == 'POST' and request.form['btn'] == 'preview':

        username=session['username']
        return redirect(url_for('preview', loggedIn=loggedIn, username=username))

    if request.method == 'POST' and request.form['btn'] == 'edit':
        username=session['username']
        return redirect(url_for('edit', loggedIn=loggedIn, username=username))


    return render_template("pages/profile.html", username=username, active="profile", loggedIn=loggedIn, commstyles=commstyles, other=other)


# Preview
@app.route('/preview/<username>', methods = ['GET', 'POST'])
def preview(username):
    """ Grab the details of the user and display them in the user_details template.
    If the user pushes the 'publish' button, the display variable is set to True, so
    that the user can now be found in searches or show up on the carousel on index.html. """

    loggedIn = True if 'username' in session else False

    if loggedIn == False:
        return redirect(url_for('forbidden'))

    user = db.profile.find_one({"username": username})

    if request.method == 'POST' and request.form['btn'] == 'publish':
        db.profile.find_one_and_update({"username": username}, {"$set": {"display": True}})

        return redirect(url_for('user_details', username=session['username'], newProfile=True ))


    if request.method == 'POST' and request.form['btn'] == 'discard':
            db.profile.update_many( {'username': username},
            { "$set": {
                'shortDescription': "",
                "imgURL": "",
                "district": "",
                "skills": [],
                "desiredSkills": [],
                "communicationStyle": [],
                "otherDetails": [],
                "published": "",
                "github": "",
                "linkedin": "",
                "twitter": ""

            }})
            username = session['username']
            flash("Your changes have been discarded.", "success")
            return redirect(url_for('newprofile', username = username, discarded=True, skills=skills,
    commstyles=commstyles, other=other))


    return render_template("pages/user_details.html", active="preview", user=user, loggedIn = loggedIn, preview=True)


# Edit Profile
@app.route('/edit/<username>', methods = ['GET', 'POST'])
def edit(username):

    loggedIn = True if 'username' in session else False

    if loggedIn == False:
        return redirect(url_for('forbidden'))

    if request.method == 'POST' and request.form['btn'] == 'save':
        db.profile.update_many( {'username': session['username']},
        { "$set": {
        'shortDescription': request.form.get('shortDescription'),
        "imgURL": request.form.get('imgURL'),
        "district": request.form.get('district'),

        }})

        return redirect(url_for('profile', loggedIn=loggedIn, username=session['username']))


    username = db.profile.find_one({"username": username})

    return render_template('pages/editprofile.html', loggedIn=loggedIn, username=username, active="profile", skills=skills,
    commstyles=commstyles, other=other)


# Logout
@app.route('/logout', methods = ['GET'])
def logout():
    """ Logs the user out of their session. """

    session.clear()

    return redirect(url_for('index'))


# User details page
@app.route('/user/<username>', methods = ['GET', 'POST'])
def user_details(username):
    """ Checks if the user is logged in to display the correct navbar configuation.
    Accepts the username variable, looks it up in the database, and passes it on to
    the html page with full user details. """

    loggedIn = True if 'username' in session else False

    user = db.profile.find_one({"username": username})

    return render_template("pages/user_details.html", user=user, active="profile", loggedIn=loggedIn)


# Custom 403 page
@app.route('/denied')
def forbidden():
    """ If a user tries to access a part of the website that for which they need
    need to be logged in, but aren't, they get redirected to the custom permission denied page. """

    return render_template("pages/forbidden.html")

if __name__ == '__main__':
    app.run(host=os.getenv('IP'), port=(os.getenv('PORT')), debug="True")
