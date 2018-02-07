##### server file ######
from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Event, Invitation, Picture, Friendship, connect_to_db, db

# from model import 


app = Flask(__name__)
app.secret_key = 'EVENTFULL'




@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')


@app.route('/login')
def login_form():
	"""Show login form."""

	return render_template('login_form.html')



@app.route('/login', methods=['POST'])
def login():
	"""Show login form."""

	email = request.form.get('user_email')
	password = request.form.get('user_password')


	user = User.query.filter(User.email == email).first()  # returns a user obj

	if user is not None and user.password == password:
		session['user_id'] = user.user_id

		flash('Successfully logged in.')
		return redirect('/user/{id}'.format(id=user.user_id))

	else:
		flash('Sorry, incorrect login.')
		return redirect('/login')


@app.route('/user/<user_id>')
def user_profile(user_id):
	"""User's account page."""

	user = User.query.filter(User.user_id == user_id).first()

	return render_template('user_profile.html', user=user)


@app.route('/registration-form')
def show_reg_form():
	"""Displays registration form."""

	return render_template('registration_form.html')


@app.route('/new-user', methods=['POST'])
def validate_user():
	"""Checks if user is already registered, if not, register new user."""

	name = request.form.get('new_user_name')
	email = request.form.get('new_user_email')
	password = request.form.get('new_user_password')
	phone = request.form.get('new_user_phone')

	validation_entry = User.query.filter(User.email == email).first()

	if validation_entry is None:
		new_user = User(name=name, email=email, password=password, phone=phone)
		db.session.add(new_user)
		db.session.commit()

		flash('Successfully registered!')
		return redirect('/')

	else:
		flash('Sorry, that email is already in use.')
		return redirect('/registration-form')



@app.route('/logout')
def logout():
    """Logs user out of website."""

    session.clear()
    flash('You have logged out.')
    return redirect('/')













if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0"),