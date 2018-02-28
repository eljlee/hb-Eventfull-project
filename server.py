##### server file ######
import os
from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for
from twilio.rest import Client
# from twilio.twiml.messaging_response import MessagingResponse
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename
import datetime
from model import User, Event, Invitation, Picture, Friendship, connect_to_db, db

# import pdb; pdb.set_trace()

# Twilio
account_sid = "ACb630b7f56b10119e369292a6afaa4449"
auth_token = "a541fec3e2e5b3e03c67d5a84c649dab"
client = Client(account_sid, auth_token)

# Uploading image file into project folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'EVENTFULL'


# NEED TO BE LOGGED IN BEFORE BEING ABLE TO DO ANYTHING?

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

        flash('Successfully logged in, {name}'.format(name=user.name))
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
    current_user_friendship = Friendship.query.filter(Friendship.friend_1_id == session['user_id'],
                                                      Friendship.friend_2_id == user_id).first()

    # used to check if user has access to another user's event and calendar
    friend_list = []
    for friend in friends:
        friend_list.append(friend.friend_2_id)


    return render_template('user_profile.html', user=user, events=events, invitations=invitations, 
                           friend_list=friend_list, current_user_friendship=current_user_friendship)


@app.route('/friending/<user_id>', methods=['POST'])
def befriending(user_id):
    """Friending between session user and another user."""


    existing_friendship = Friendship.query.filter(Friendship.friend_1_id == session['user_id'],
                                                  Friendship.friend_2_id == user_id).first()

    if not existing_friendship:
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


@app.route('/unfriending/<user_id>', methods=['POST'])
def unfriending(user_id):
    """Unfriend another user."""

    existing_friendship = Friendship.query.filter(Friendship.friend_1_id == session['user_id'],
                                                  Friendship.friend_2_id == user_id).first()

    if existing_friendship:
        db.session.delete(existing_friendship)
        db.session.commit()

    return redirect('/user/{user_id}'.format(user_id=user_id))


@app.route('/search-friend', methods=['POST'])
def fine_specific_user():
    """Find specific user's by email."""

    email = request.form.get('email')  

    user = User.query.filter(User.email == email).first()

    return redirect('/user/{user_id}'.format(user_id=user.user_id))


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

    # get file class of image
    image = request.files['image']
    if image:
        # get actual file name
        filename = secure_filename(image.filename)
        user.image = filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

    return "Calendar event."


@app.route('/db-events.json/<user_id>')
def get_events_from_db(user_id):
    """Return all events from db for specific user as JSON."""

    # this should get all invitations user has been invited to
    invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    # should get all the events user has created
    hostings = Event.query.filter(Event.creator_id == user_id).all()

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


# Keep?
# @app.route("/sms", methods=['GET', 'POST'])
# def sms_ahoy_reply():
#     """Respond to incoming messages with a friendly SMS."""
#     # Start our response
#     resp = MessagingResponse()

#     # Add a message
#     resp.message("Ahoy! Thanks so much for your message.")

#     return str(resp)


# EVENT INFORMATION
##############################################################
@app.route('/event-page/<event_id>')
def event_info(event_id):
    """Display event info."""

    personal_invitation = Invitation.query.filter(Invitation.invitee_id == session['user_id'], 
                                                  Invitation.event_id == event_id).first()
    event_info = Event.query.filter(Event.event_id == event_id).one()

    invitations = Invitation.query.filter(Invitation.event_id == event_id).all()

    pictures = Picture.query.filter(Picture.event_id == event_id).all()


    # if event_info.creator_id != session['user_id'] and personal_invitation.attending != True and personal_invitation.attending != False:
    #     return render_template('invitation.html', event_info=event_info)

    # else:
    return render_template('event_page.html', invitations=invitations, event_info=event_info, 
                           pictures=pictures, personal_invitation=personal_invitation)


@app.route('/invite-reply/<event_id>', methods=['POST'])
def invitations(event_id):
    """Replying to invititation."""

    invitation = Invitation.query.filter(Invitation.event_id == event_id).first()

    reply_str = request.form.get('reply')
    invitation.attending = reply_str == 'yes'

    invitation.notes = request.form.get('note')

    db.session.commit()

    return redirect('/event-page/{event_id}'.format(event_id=invitation.event_id))


@app.route('/upload-photos/<event_id>', methods=['POST'])
def upload_photos(event_id):
    """Upload photos to particular event."""

    # gets a file class object
    image = request.files['image']
    # get actual file name
    filename = secure_filename(image.filename)
    # save file into my folder
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_photo = Picture(
        filename=filename,
        uploader_id=session['user_id'],
        event_id=event_id
        )

    db.session.add(new_photo)
    db.session.commit()

    return redirect('/event-page/{event_id}'.format(event_id=event_id))


@app.route('/invite-more/<event_id>', methods=['POST'])
def invite_more_guests(event_id):
    """Invite more friends on the event page."""


    invitees = request.form.getlist('friend')

    already_invited = Invitation.query.filter(Invitation.event_id == event_id,
                                         Invitation.invitee_id.in_(invitees)).all()

    already_invited_ids = [str(invitation.invitee_id) for invitation in already_invited]

    for invitee in invitees:
        if invitee in already_invited_ids:
            print "Already added this user {id}".format(id=invitee)
            continue

        invitation = Invitation(
                                invitee_id=invitee,
                                event_id=event_id,
                                )

        db.session.add(invitation)
        db.session.commit()


    return redirect('/event-page/{event_id}'.format(event_id=event_id))

# # HOW DO I TEST FOR THIS?
# @app.route('/invite-notification/<event_id>')
# def invite_text(event_id):
#     """Sends a notificaiton via text."""

#      # by inivitations joined at that one event?
#     invitations = Invitation.query.filter(Invitation.event_id == event_id).all()

#     for user in invitations:
#         client.api.account.messages.create(
#             to="+1415" + str({{ user.invitee.phone }}),
#             from_="+14158516073 ",
#             body="You have an invite from {{ invitations.event.creator.name }}!\nCheck it out at http://localhost:5000/event/{{ event.event_id }}"
#             )

#     return invitations.event.creator.name


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
    image = 'default-placeholder.png'

    validation_entry = User.query.filter(User.email == email).first()

    if validation_entry is None:
        # without phone number; would error out if trying to instantiate new User with an empty phone attribute
        if phone == '' :
            new_user = User(
                name=name,
                email=email,
                password=password,
                image=image
                )
            
        # with phone number
        else:
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
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0"),