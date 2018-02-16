##### server file ######
from flask import Flask, render_template, redirect, request, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Event, Invitation, Picture, Friendship, connect_to_db, db

# import pdb; pdb.set_trace()


app = Flask(__name__)
app.secret_key = 'EVENTFULL'




@app.route('/')
def homepage():
    """Show homepage."""

    return render_template('homepage.html')

# @app.before_request
# def before_request():
#   g.session = session


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

    user = User.query.filter(User.user_id == user_id).first()
    invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    events = Event.query.filter(Event.creator_id == user_id).all()

    return render_template('user_profile.html', user=user, events=events, invitations=invitations)


@app.route('/user/<user_id>', methods=['POST'])
def profile_pic(user_id):
    """User can upload profile image."""

    user.image = request.form.get('pic')

    user = User.query.filter(User.user_id == user_id).first()
    invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    events = Event.query.filter(Event.creator_id == user_id).all()

    db.session.commit()

    return render_template('user_profile.html', user=user, events=events, invitations=invitations)


@app.route('/calendar-events')
def get_events_from_db():
    """Return all events for specific user as JSON."""

    # import pdb; pdb.set_trace()

    # this should get all invitations user has been invited to
    invited_events = Invitation.query.filter(Invitation.invitee_id == session['user_id']).all()

    events = []

    for invited_event in invited_events:
        event_info = {}
        event_info = {
            'start_date': str(invited_event.event.start_at), 
            'end_date': str(invited_event.event.end_at), 
            'text': str(invited_event.event.title)
            }

        events.append(event_info)
    print events
    results = {'result': events}
    return jsonify(results)


# @app.route('/edit-profile')
# def edit_profile():
#     """User can make changes in their profile."""


#     return render_template('user_profile.html', )



# CREATE EVENT
##############################################################
@app.route('/create-event')
def creating_event_form():
    """Displays form to create an event."""

    users = User.query.all()

    return render_template('create_event_form.html', users=users)


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

    if event_info.creator_id != session['user_id'] and personal_invitation.attending == None:
        return render_template('invitation.html', event_info=event_info)

    else:
        return render_template('event_page.html', invitations=invitations, event_info=event_info)


@app.route('/invite-reply', methods=['POST'])
def invitations():
    """Replying to invititation."""

    # NEED TO FIX, NEED CORRECT EVENT_ID

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