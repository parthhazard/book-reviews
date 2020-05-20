# -*- coding: utf-8 -*-
import os
from flask import Flask, session, render_template, redirect, url_for, session, logging, request, flash, jsonify, make_response
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, StringField, SelectField, PasswordField, validators, SelectMultipleField, DecimalField, TextAreaField
from wtforms.validators import ValidationError
from passlib.hash import sha256_crypt
from extra_functions import password_val, time_diff, time_small
from random import randint
from wtforms import widgets
from functools import wraps
from datetime import datetime
import pytz
import requests

# def create_app():

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
goodreadsKey = 'OPzZU454Ppen5M5rnjmYVw'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"), pool_size=20, max_overflow=20)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    return render_template('home.html')

# Login Protocols
def isLoggedIn(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            error = 'Unauthorized. Login to Continue'
            return render_template('login.html', error=error)
    return wrapped

def isNotLoggedIn(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            error = 'Already Logged In. To logon with another account, Logout first'
            flash(error, 'danger')
            return redirect(url_for('dashboard'))
    return wrapped

# Error Page
@app.route('/error')
def pageNotFound():
    return render_template('error.html'), 404

# registration
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class registrationForm(Form):
    name = StringField('Name', [
        validators.DataRequired(),
        validators.Length(max=70)
    ])
    username = StringField('Username', [
        validators.Length(max=50),
        validators.DataRequired()
    ])
    def validate_username(form, field):
        user = db.execute("SELECT username FROM users WHERE username = :username", {"username": field.data}).fetchone()
        if user:
            raise ValidationError("Username already in use.")

    pwd = PasswordField('Password', [
        validators.DataRequired(),
        password_val,
        validators.EqualTo('confirm', message="Passwords do not match.")
    ])
    confirm = PasswordField('Confirm Password')

    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')])

    country = StringField('Country', [validators.DataRequired()])
    state = StringField('State', [validators.DataRequired()])
    city = StringField('City', [validators.DataRequired()])

    profession = StringField('Profession', [validators.DataRequired()])

    genre_list = ['Action and Adventure', 'Alternate History', 'Art', 'Autobiography', 'Biography', 'Cookbook', 'Crime', 'Diary', 'Drama', 'Fantasy', 'Graphic Novel', 'Health', 'History', 'Horror', 'Mystery',
        'Poetry', 'Religion and Spirituality', 'Romance', 'Satire', 'Science Fiction', 'Self Help', 'Short Story', 'Suspense', 'Thriller', 'Travel', 'True Crime']

    genres = MultiCheckboxField('Favourite Genres', choices = [(genre, genre) for genre in genre_list])


@app.route("/register", methods=['GET', 'POST'])
@isNotLoggedIn
def regist():
    form = registrationForm(request.form)
    if (request.method == 'POST') and (form.validate()):
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.pwd.data))
        gender = form.gender.data
        location = ",  ".join([form.city.data, form.state.data, form.country.data])
        prof = form.profession.data
        genres = list(form.genres.data)
        # generate id

        res = db.execute("SELECT * FROM users").fetchall()
        id_list = [x['id'] for x in res]
        while True:
            id = randint(10000, 999999)
            if id not in id_list:
                break

        # add user to db
        db.execute("INSERT INTO users(id, name, username, password, gender, genres, location, profession) VALUES(:id, :name, :username, :pwd, :gender, :genres, :location, :prof)",
            {"id": id, "name": name, "username": username, "pwd": password, "gender": gender, "genres": genres, "location": location, "prof": prof})
        db.commit()
        flash('The user is registered', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# Login form class

@app.route("/login", methods=['GET', 'POST'])
@isNotLoggedIn
def login():
    if request.method == 'POST':
        # get user fed login credentials
        username = request.form['username']
        pwd_inp = request.form['password']

        # verify login credentials
        res = db.execute("SELECT * FROM users WHERE username = :user", {"user": username}).fetchone()

        # verify username
        if res:
            pwd_ver = res['password']
            # verify password
            if sha256_crypt.verify(pwd_inp, pwd_ver):
                session['logged_in'] = True
                session['user_id'] = res['id']
                return redirect(url_for('dashboard'))
            else:
                error = "Incorrect Password. Try Again"
                flash(error, 'danger')
                redirect(url_for('login'))
        else:
            error = "No such user exists."
            flash(error, 'danger')
            redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@isLoggedIn
def dashboard():
    user_id = session['user_id']
    usersQuery = db.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
    reviewQuery = db.execute("SELECT * FROM reviews WHERE (tags IN ('public', 'archived')) AND user_id = :id", {"id": user_id}).fetchall()
    for x in reviewQuery:
        db.execute("UPDATE reviews SET current_time_diff = :diff WHERE id= :id", {"diff": time_diff(x['posted_date']), "id": x['id']})
        db.execute("UPDATE reviews SET current_time_str = :small WHERE id= :id", {"small": time_small(x['posted_date']), "id": x['id']})
    db.commit()
    reviewQuery = db.execute("SELECT reviews.*, books.title FROM reviews INNER JOIN books ON reviews.isbn = books.isbn WHERE reviews.user_id = :id ORDER BY posted_date DESC", {"id": user_id}).fetchall()
    return render_template('dashboard.html', users=usersQuery, reviews=reviewQuery)


@app.route('/logout')
@isLoggedIn
def logout():
    session.clear()
    flash('You are logged out.', 'success')
    return redirect(url_for('login'))

# Book Page

@app.route('/books/<string:isbn>')
def bookPage(isbn):
    # reviews average rating???
    books = db.execute("SELECT books.title, books.publication_year, books.isbn, authors.name FROM books INNER JOIN authors ON books.author_id=authors.id WHERE books.isbn = :isbn", {"isbn": str(isbn)}).fetchone()
    # if isbn for book exists
    if books:
        userReview = False
        reviews = db.execute("SELECT reviews.*, users.username FROM reviews INNER JOIN users ON reviews.user_id=users.id WHERE isbn = :isbn AND tags = :tag", {"isbn": str(isbn), "tag": "public"}).fetchall()
        # if user logged in
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreadsKey, "isbns": isbn})
        result = res.json()
        res = result['books'][0]
        if 'logged_in' in session:
            # if user has a review for this book
            for review in reviews:
                if session['user_id'] == review['user_id']:
                    if review['tags'] == 'public':
                        userReview = True
                        break
        return render_template('books.html', book = books, reviews = reviews, ifUserReview=userReview, res=res)
    else:
        error = "There is no book with is ISBN."
        flash(error, "danger")
        return redirect(url_for('home'))


# Add review only if logged in

@app.route('/addreview', methods=['POST'])
@isLoggedIn
def addReview():
    if request.method == 'POST':
        rating = request.form['rating']
        reviewText = request.form['reviewText']
        reviewText = reviewText.replace("\n", " ")
        reviewText = reviewText.replace("\r", " ")
        isbn = request.form['isbn']
        url = "books/"+str(isbn)
        if (float(rating) > 5) or (len(str(reviewText).split(" "))>500):
            error = "You have not met the review guidelines. Fix your error."
            flash(error, 'danger')
        else:
            db.execute("INSERT INTO reviews(isbn, user_id, ratings, review_text, tags) VALUES(:isbn, :user, :rating, :review, :tag)", {"isbn": isbn, "user": session['user_id'], "rating": rating, "review": reviewText, "tag": "public"})
            db.commit()
            flash("The review is added.", 'success')
    return redirect(url)


#Update existing review
@app.route('/updatereview/<int:id>', methods=['POST'])
@isLoggedIn
def updateReview(id):
    if request.method == 'POST':
        oldrating = request.form['oldrating']
        rating = request.form['rating']
        oldreviewText = request.form['oldreviewText']
        reviewText = request.form['reviewText']
        reviewText = reviewText.replace("\n", " ")
        reviewText = reviewText.replace("\r", " ")
        if (float(rating) > 5) or (len(str(reviewText).split(" "))>500):
            error = "You have not met the review guidelines. Fix your error."
            flash(error, 'danger')
        elif (oldrating == rating) and (oldreviewText == reviewText):
            error = "No chnages made to existing rating"
            flash(error, 'danger')
        else:
            if oldrating == rating :
                db.execute("UPDATE reviews SET review_text=:review WHERE id=:id", {"review": reviewText, "id": id})
            elif oldreviewText == reviewText:
                db.execute("UPDATE reviews SET ratings=:rating WHERE id=:id", {"rating": rating, "id": id})
            else:
                db.execute("UPDATE reviews SET ratings=:rating, review_text=:review WHERE id=:id", {"rating": rating, "review": reviewText, "id": id})
            flash("The changes made to the review has been updated.", 'success')
    db.commit()
    return redirect(url_for('dashboard'))

# deleting a review
@app.route('/delete', methods = ['POST'])
@isLoggedIn
def deleteReview():
    if request.method == 'POST':
        isbn = request.form['isbn']
        review_id = request.form['review_id']
        db.execute("DELETE FROM reviews WHERE isbn=:isbn AND id=:review_id", {"isbn": isbn, "review_id": review_id})
    db.commit()
    return redirect(url_for('dashboard'))

# deleteing all reviews for userReview
@app.route('/deleteall', methods = ['POST'])
@isLoggedIn
def deleteAll():
    if request.method == 'POST':
        db.execute("DELETE FROM reviews WHERE user_id=:id", {"user_id": session['user_id']})
    db.commit()
    return redirect(url_for('dashboard'))

# archiving a review
@app.route('/archive', methods = ['POST'])
@isLoggedIn
def archiveReview():
    if request.method == 'POST':
        isbn = request.form['isbn']
        review_id = request.form['review_id']
        db.execute("UPDATE reviews SET tags= CASE WHEN tags='archived' THEN 'public' WHEN tags='public' THEN 'archived' END WHERE isbn=:isbn AND id=:review_id", {"isbn": isbn, "review_id": review_id})
    db.commit()
    return redirect(url_for('dashboard'))

# Archive all Reviews
@app.route('/archiveall', methods = ['POST'])
@isLoggedIn
def archiveAll():
    if request.method == 'POST':
        db.execute("UPDATE reviews SET tags= CASE WHEN tags='public' THEN 'archived' WHEN tags='archived' THEN 'public' END WHERE user_id=:user", {"user": session['user_id']})
    db.commit()
    return redirect(url_for('dashboard'))


# api to produce resulting json

@app.route('/api/<string:isbn>', methods=['GET'])
def api_json(isbn):
    if request.method == 'GET':
        book = db.execute("SELECT books.isbn, books.title, books.publication_year, authors.name FROM books INNER JOIN authors ON books.author_id = authors.id WHERE books.isbn=:isbn", {"isbn": isbn}).fetchone()
        if book:
            reviews = db.execute("SELECT COUNT(*), AVG(ratings) FROM reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
            result = jsonify(title=book['title'], author=book['name'], year=book['publication_year'], isbn=book['isbn'], review_count = reviews['count'], average_score=str(round(reviews['avg'], 2)))
            return result
        else:
            return redirect(url_for('pageNotFound'))

# search

@app.route('/search', methods=["POST"])
def search():
    if request.method == 'POST':
        q = request.form['searchQuery'].strip()
        if len(q) == 1:
            result = False
            error = 'minimum query length must be 2'
            render_template('search.html', results=result, query=q, error=error)
        else:
            query_list = q.split(" ")
            for i in range(len(query_list)):
                query_list[i] = query_list[i] + ":*" + " & "
            query_list = "".join(query_list)
            query_list = query_list[:-3]

            result = db.execute("SELECT books.isbn, books.title, authors.name FROM books INNER JOIN authors ON books.author_id=authors.id, to_tsquery(:queryTsv) AS query WHERE (SIMILARITY(METAPHONE(books.title, 12), METAPHONE(:query, 12))>0.3) OR (query @@ books.tsv AND ts_rank_cd(books.tsv, query)>0.1) OR (query @@ authors.tsv AND ts_rank_cd(authors.tsv, query)>0.1) OR (SIMILARITY(METAPHONE(authors.name, 10), METAPHONE(:query, 10))>0.3) ORDER BY ts_rank_cd(books.tsv, query) DESC, ts_rank_cd(authors.tsv, query) DESC, SIMILARITY(METAPHONE(books.title, 12), METAPHONE(:query, 12)) DESC, SIMILARITY(METAPHONE(authors.name, 10), METAPHONE(:query, 10)) DESC LIMIT 30", {"query": q, "queryTsv": query_list}).fetchall()

    return render_template('search.html', results=result, query=q)
    # return app


# if __name__ == "__application__":
#     app = create_app()
#     app.run()
