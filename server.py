"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route("/users/<user_id>")
def user_info(user_id):
    """Show information for user."""

    ratings = Rating.query.filter_by(user_id=user_id).all()
    info = User.query.filter_by(user_id=user_id).one()

    return render_template("user_info.html", ratings=ratings, info=info)

@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)

@app.route("/movies/<movie_id>")
def movie_info(movie_id):
    """Show information for movie."""
    movie = Movie.query.filter_by(movie_id=movie_id).one()
    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    return render_template("movie_info.html", movie=movie, ratings=ratings)

@app.route("/movie/rate/<movie_id>", methods=["POST"])
def rate_movie(movie_id):
    rating = request.form.get("rating")
    user_id = session["user_id"]
    new_rating = Rating(movie_id=movie_id, score=rating, user_id=user_id)

    db.session.add(new_rating)
    db.session.commit()
    redirect_url = "/movies/" + str(movie_id)

    return redirect(redirect_url)

@app.route("/register", methods=["GET"])
def register_form():

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():

    email = request.form.get("email")
    password = request.form.get("password")

    new_user = User(email=email, password=password)

    db.session.add(new_user)
    db.session.commit()
    return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_process():

    email = request.form.get("email")
    password = request.form.get("password")

    existing_email = User.query.filter_by(email=email).one()
    if email == existing_email.email:
        if password == existing_email.password:
            session['user_id'] = existing_email.user_id
            session['email'] = existing_email.email
            flash('You were successfully logged in')
            redirect_url = "/users/" + str(existing_email.user_id)
            return redirect(redirect_url)

    else:
        flash('Invalid login or password')

    
    return redirect("/login")


@app.route("/logout")
def logout():
    
    session.clear()
    flash('You were successfully logged out!')
    return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
