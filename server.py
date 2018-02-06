##### server file ######
from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db
# from model import 


app = Flask(__name__)
app.secret_key = 'EVENTFUL'


@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')


@app.route('/login')
def login_form():
	"""Show login form."""

	return render_template('login_form.html')


@app.route('/login', methods='POST')
def login():
	"""Show login form."""

	email = request.form.get('user_email')
	password = request.form.get('user_password')

	user = User.query.filter(User.email == email).first()  # returns a user obj

	if user is not None and user.password == password:
		session['user_id'] = user.user_id

		return 'yay'

	else:
		return redirect('/login')















if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0"),