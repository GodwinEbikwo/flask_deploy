import secrets
from utils import get_top_artists, sp_oauth, userProfile
from datetime import datetime
from flask import Flask, render_template, redirect, request, session

sp_oauth = sp_oauth


# initialise the flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return render_template("login.html", auth_url=auth_url)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    session["token_info"] = token_info
    return redirect("/")


@app.route("/")
def index():
    token_info = session.get("token_info")
    if not token_info or token_info["expires_at"] < datetime.now().timestamp():
        return redirect("/login")

    user = userProfile()
    top_artists = get_top_artists(time_range="short_term", limit=6)

    return render_template("index.html", user=user, top_artists=top_artists)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
