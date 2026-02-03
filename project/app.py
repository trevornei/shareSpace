from functools import wraps
from flask import (
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from project.config import app, db
from project import models


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["POST"])
def add_entry():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Post(request.form["title"], request.form["text"])
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == "POST":
        user = db.session.query(models.User).filter_by(name=request.form["username"]).first()
        if  not user or user.password != request.form["password"]:
            error = "Invalid username or password"
        else:
            # Can add to userInfo dict to include more info later
            userInfo = {
                "username": user.name
            }
            session["logged_in"] = True
            session["userInfo"] = userInfo
            flash("You were logged in")
            return redirect(url_for("index"))
    return render_template("login.html", error=error)

@app.route("/newuser", methods=["GET", "POST"])
def new_user():
    if request.method == "POST" and request.form.get("password") and request.form.get("username"):
        newuser = models.User(request.form["username"], request.form["password"])
        try:
            db.session.add(newuser)
            db.session.commit()
            userInfo = {
                "username": newuser.name
            }
            session["logged_in"] = True
            session["userInfo"] = userInfo
            flash("New User Created")
            return redirect(url_for("index"))
        except Exception as e:
            return render_template("newuser.html", error="Error when adding user: " + str(e))
    else:
        return render_template("newuser.html")

@app.route("/profile")
def profile():
    """User profile page."""
    return render_template("profile.html")
    pass

@app.route("/logout")
def logout():
    """User logout/authentication/session management."""
    session.pop("logged_in", None)
    flash("You were logged out")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {"status": 0, "message": "Error"}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {"status": 1, "message": "Post Deleted"}
        flash("The entry was deleted.")
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
    return jsonify(result)


@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")


if __name__ == "__main__":
    app.run()
