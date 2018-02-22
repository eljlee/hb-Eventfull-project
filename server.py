##### server file ######
from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename
import datetime
from model import User, Event, Invitation, Picture, Friendship, connect_to_db, db

# import pdb; pdb.set_trace()

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'EVENTFULL'




@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')


# LOGGING IN
##############################################################
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


# USER PROFILE
##############################################################
@app.route('/user')
def valid_user():
    """Checks if there's a valid login to redirect"""

    if 'user_id' in session:
        return redirect('/user/{id}'.format(id=session['user_id']))

    else:
        flash('Log in first.')
        return redirect('/login')


@app.route('/user/<user_id>')
def user_profile(user_id):
    """User's account page."""

    # gathering user info, events invited to and created, and their friends
    # to be displayed onto their profile page
    user = User.query.filter(User.user_id == user_id).first()
    invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    events = Event.query.filter(Event.creator_id == user_id).all()
    friends = Friendship.query.filter(Friendship.friend_1_id == user_id).all()

    return render_template('user_profile.html', user=user, events=events, invitations=invitations, friends=friends)


@app.route('/friending/<user_id>', methods=['POST'])
def befriending(user_id):
    """Friending between session user and another user."""

    # creating friendship one way
    new_friendship = Friendship(
        friend_1_id = session['user_id'],
        friend_2_id = user_id
        )
    
    # and then the other way
    other_way = Friendship(
        friend_1_id = user_id,
        friend_2_id = session['user_id']
        )

    db.session.add(new_friendship)
    db.session.add(other_way)
    db.session.commit()

    flash('Made a friend!')

    return redirect('/user/{user_id}'.format(user_id=user_id))


# USER PROFILE - EDIT
#############################################################
@app.route('/edit-profile/<user_id>')
def edit_profile_template(user_id):
    """Profile edit template."""

    user = User.query.filter(User.user_id == session['user_id']).first()

    return render_template('edit_profile.html', user=user)


@app.route('/edit-profile/<user_id>', methods=['POST'])
def edit_profile(user_id):
    """Editing profile."""

    user = User.query.filter(User.user_id == session['user_id']).first()

    if request.form.get('name'):
        user.name = request.form.get('name')
    if request.form.get('email'):
        user.email = request.form.get('email')
    if request.form.get('phone'):
        user.phone = request.form.get('phone')

    # upload image
    if request.form.get('image'):
        filename = secure_filename(file.filename)
        user.image = filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db.session.commit()

    return redirect('/user/{user_id}'.format(user_id=session['user_id']))




# ACTIVITIES ON CALENDAR
##############################################################
@app.route('/calendar-events', methods=['POST'])
def get_events_from_cal():
    """Recieve events made on calendar, and udpate db."""

    title = request.form.get('title')
    start = str(request.form.get('start_date'))
    day, month, date, year, time, blank1, zone = start.split()
    start_time = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    print start_time

    end = str(request.form.get('end_date'))
    day, month, date, year, time, blank1, zone = end.split()
    end_time = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    print end_time

    new_event = Event(
        title=title,
        start_at=start_time, 
        end_at=end_time,
        creator_id=session['user_id']
        )
    db.session.add(new_event)
    db.session.commit()

    return "Okay"


@app.route('/db-events.json')
def get_events_from_db():
    """Return all events from db for specific user as JSON."""

    # this should get all invitations user has been invited to
    invitations = Invitation.query.filter(Invitation.invitee_id == session['user_id']).all()
    # should get all the events user has created
    hostings = Event.query.filter(Event.creator_id == session['user_id']).all()

    events_invited = []
    for invitation in invitations:
        event_info = {}
        event_info = {
            'start_date': str(invitation.event.start_at), 
            'end_date': str(invitation.event.end_at), 
            'text': str(invitation.event.title)
            }

        events_invited.append(event_info)

    events_hosting = []
    for hosting in hostings:
        event_info = {}
        event_info = {
            'start_date': str(hosting.start_at), 
            'end_date': str(hosting.end_at), 
            'text': str(hosting.title)
            }

        events_hosting.append(event_info)


    # made into a single key-value dict of a list of dicts
    results = {'invites': events_invited, 'hostings': events_hosting}
    return jsonify(results)


# CREATE EVENT
##############################################################
@app.route('/create-event')
def creating_event_form():
    """Displays form to create an event."""

    user = User.query.filter(User.user_id == session['user_id']).first()

    return render_template('create_event_form.html', user=user)


@app.route('/create-event', methods=['POST'])
def create_event():
    """Register new event."""

    title = request.form.get('title')
    start_time = request.form.get('start_date')
    end_time = request.form.get('end_date')

    public_str = request.form.get('public')
    public = public_str == 'public'

    new_event = Event(
        title=title,
        start_at=start_time, 
        end_at=end_time,
        creator_id=session['user_id'], 
        public=public
        )
    db.session.add(new_event)
    db.session.commit()


    invitees = request.form.getlist('friend')
    for invitee in invitees:
        invitation = Invitation(
                                invitee_id=invitee,
                                event_id=new_event.event_id,
                                )

        db.session.add(invitation)
        db.session.commit()

    flash('Event created!')

    return redirect('/event-page/{id}'.format(id=new_event.event_id))



# EVENT INFORMATION
##############################################################
@app.route('/event-page/<event_id>')
def event_info(event_id):
    """Display event info."""

    personal_invitation = Invitation.query.filter(Invitation.invitee_id == session['user_id'], 
                                                  Invitation.event_id == event_id).first()
    event_info = Event.query.filter(Event.event_id == event_id).one()

    invitations = Invitation.query.filter(Invitation.event_id == event_id).all()

    if event_info.creator_id != session['user_id'] and personal_invitation.attending != True and personal_invitation.attending != False:
        return render_template('invitation.html', event_info=event_info)

    else:
        return render_template('event_page.html', invitations=invitations, event_info=event_info)


@app.route('/invite-reply/<event_id>', methods=['POST'])
def invitations(event_id):
    """Replying to invititation."""

    invitation = Invitation.query.filter(Invitation.event_id == event_id).first()

    reply_str = request.form.get('reply')
    invitation.attending = reply_str == 'yes'

    invitation.notes = request.form.get('note')

    db.session.commit()

    return redirect('/event-page/{event_id}'.format(event_id=invitation.event_id))


# NEW USERS
##############################################################
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
    image = 'http://cumbrianrun.co.uk/wp-content/uploads/2014/02/default-placeholder.png'

    validation_entry = User.query.filter(User.email == email).first()

    if validation_entry is None:
        new_user = User(
            name=name,
            email=email,
            password=password,
            phone=phone,
            image=image
            )
        db.session.add(new_user)
        db.session.commit()

        flash('Successfully registered, {name}!'.format(name=name))
        return redirect('/')

    else:
        flash('Sorry, that email is already in use.')
        return redirect('/registration-form')


##############################################################
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