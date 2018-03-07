##### server file ######
# import ipdb; ipdb.set_trace()

#################
#### imports ####
#################
import os
from flask import Flask, render_template, redirect, request, flash, session, jsonify, url_for
# from flask_login import login_required
# @login_required
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug import secure_filename
import datetime
from model import User, Event, Invitation, Picture, Friendship, connect_to_db, db
import helpers


################
#### config ####
################
# Uploading image file into project folder
UPLOAD_FOLDER = 'static/picture_uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'EVENTFULL'


################
#### routes ####
################

# NEED TO BE LOGGED IN BEFORE BEING ABLE TO DO ANYTHING?

@app.route('/')
def homepage():
    """Show homepage."""
    # if 'user_id' in session:
    #     return redirect('/user')

    # else:
    return render_template('homepage.html')


# LOGGING IN
##############################################################
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
        return redirect('/')


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

    if not session:
        flash('Sorry, incorrect login.')
        return redirect('/')
    
    now = datetime.datetime.today()
    # gathering user info, events invited to and created, and their friends
    # to be displayed onto their profile page
    user = User.query.filter(User.user_id == user_id).first()
    events = Event.query.filter(Event.creator_id == user_id).all()
    invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    
    friends = Friendship.query.filter(Friendship.friend_1_id == user_id).all()
    current_user_friendship = Friendship.query.filter(Friendship.friend_1_id == session['user_id'],
                                                      Friendship.friend_2_id == user_id).first()

    upcoming_events = []
    for invitation in invitations:
        if invitation.event.end_at > now and invitation.attending == True:
            upcoming_events.append(invitation)
    upcoming_events.reverse()

    # used to check if user has access to another user's event and calendar
    friend_list = []
    for friend in friends:
        friend_list.append(friend.friend_2_id)


    return render_template('user_profile.html', user=user, events=events, 
                           invitations=invitations, upcoming_events=upcoming_events, 
                           friend_list=friend_list, current_user_friendship=current_user_friendship)


# @app.route('/user/events/<user_id>')
# def events_of_user(user_id):
#     """Events that relate to user."""

    
#     user = User.query.filter(User.user_id == user_id).first()
#     invitations = Invitation.query.filter(Invitation.invitee_id == user_id).all()
    

#     upcoming_events = []
#     for invitation in invitations:
#         if invitation.event.end_at > now and invitation.attending == True:
#             upcoming_events.append(invitation)
#     upcoming_events.reverse()

#     return render_template('user_events.html', )


# USER PROFILE - EDIT
#############################################################
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


# FRIENDING // UNFRIENDING // SEARCHING
##############################################################
@app.route('/friending/<user_id>', methods=['POST'])
def befriending(user_id):
    """Friending between session user and another user."""



    existing_friendship = Friendship.query.filter(Friendship.friend_1_id == session['user_id'],
                                                  Friendship.friend_2_id == user_id).first()
    session_user = User.query.filter(User.user_id == session['user_id']).first()
    other_user = User.query.filter(User.user_id == user_id).first()

    if not existing_friendship:
        # Creating friendship one way.
        new_friendship = Friendship(
            friend_1_id = session['user_id'],
            friend_2_id = user_id
            )
        db.session.add(new_friendship)

        # Friending txt notification.

        body="{friend_name}, {user_name} has befriend you. "\
        "Go to their profile and check out their calendar: http://localhost:5000/user/{user_id}".format(
                                                                                                        friend_name=other_user.name,
                                                                                                        user_name=session_user.name,
                                                                                                        user_id=session_user.user_id)
        helpers.send_txt_notification(body)
        db.session.commit()
    

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

    if session:
        email = request.form.get('email')  

        user = User.query.filter(User.email == email).first()

        return redirect('/user/{user_id}'.format(user_id=user.user_id))
    else:
        flash('Log in first!')
        return redirect('/')



# ACTIVITIES ON CALENDAR
##############################################################
@app.route('/calendar-events', methods=['POST'])
def get_events_from_cal():
    """Recieve events made on calendar, and udpate db."""

    title = request.form.get('title')
    location = request.form.get('location')
    start = str(request.form.get('start_date'))
    day, month, date, year, time, blank1, zone = start.split()
    start_time = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M')

    end = str(request.form.get('end_date'))
    day, month, date, year, time, blank1, zone = end.split()
    end_time = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M')

    new_event = Event(
        title=title,
        location=location,
        start_at=start_time, 
        end_at=end_time,
        creator_id=session['user_id'],
        )
    db.session.add(new_event)
    db.session.commit()

    return redirect('/user/{user_id}'.format(user_id=session['user_id']))

@app.route('/update-event', methods=['POST'])
def editing_event():
    """Allowed to makes changes to an event (on calendar?)."""

    event_id = request.form.get('event_id')
    cal_event_db_event = Event.query.filter(Event.event_id == event_id).first()

    cal_event_db_event.title = request.form.get('title')
    cal_event_db_event.location = request.form.get('location')
    start = str(request.form.get('start_date'))
    day, month, date, year, time, blank1, zone = start.split()
    cal_event_db_event.start_at = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M')

    end = str(request.form.get('end_date'))
    day, month, date, year, time, blank1, zone = end.split()
    cal_event_db_event.end_at = datetime.datetime.strptime(year + month + date + time, '%Y%b%d%H:%M:%S').strftime('%Y-%m-%d %H:%M')

    db.session.commit()

    return redirect('/user/{user_id}'.format(user_id=session['user_id']))


@app.route('/delete-event/<event_id>', methods=['POST'])
def delete_event(event_id):
    """Allowed to delete an event."""
    
    if request.form.get('event_id'):
        event_id = request.form.get('event_id')
    
    cal_event_db_event = Event.query.filter(Event.event_id == event_id).first()

    db.session.delete(cal_event_db_event)
    db.session.commit()

    return redirect('/user/{user_id}'.format(user_id=session['user_id']))


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
            'text': str(invitation.event.title),
            'event_location': str(invitation.event.location),
            'start_date': str(invitation.event.start_at), 
            'end_date': str(invitation.event.end_at), 
            'event_id': invitation.event_id,
            'creator_id': invitation.event.creator_id
            }

        events_invited.append(event_info)

    events_hosting = []
    for hosting in hostings:
        event_info = {}
        event_info = {
            'text': str(hosting.title),
            'event_location': str(hosting.location),
            'start_date': str(hosting.start_at), 
            'end_date': str(hosting.end_at), 
            'event_id': hosting.event_id,
            'creator_id': hosting.creator_id
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
    location = request.form.get('location')
    start_time = request.form.get('start_date')

    end_time = request.form.get('end_date')
    note = request.form.get('note)')

    new_event = Event(
        title=title,
        location=location,
        start_at=start_time, 
        end_at=end_time,
        note=note,
        creator_id=session['user_id']
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

        # send personalized text notification
        user = User.query.filter(User.user_id == invitee).first()
        event = Event.query.filter(Event.event_id == new_event.event_id).first()
        body="Hey {name}, you have an invite from {creator}!\nCheck it out at http://localhost:5000/event/{event_id}".format(
                                                                                                                             name=user.name,
                                                                                                                             creator=event.creator.name, 
                                                                                                                             event_id=event.event_id
                                                                                                                             )

        helpers.send_txt_notification(body)

    flash('Event created!')

    return redirect('/event-page/{id}'.format(id=new_event.event_id))


@app.route('/edit-event/<event_id>', methods=['POST'])
def edit_event_info(event_id):
    """Let's creator edit event info."""

    event = Event.query.filter(Event.event_id == event_id).first()

    if request.form.get('title'):
        event.title = request.form.get('title')
    if request.form.get('location'):
        event.location = request.form.get('location')
    if request.form.get('start_date'):
        event.start_at = request.form.get('start_date')
    if request.form.get('end_date'):
        event.end_at = request.form.get('end_date')
    if request.form.get('note'):
        event.note = request.form.get('note')


    db.session.commit()

    return redirect('/event-page/{event_id}'.format(event_id=event.event_id))



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

    # event_start = event_info.start_at
    # print event_start


    # start_time = event_start.strptime(event_start, '%Y-%m-%d %H:%M').strftime('%A, %d %b %Y %l:%M %p')
    # print start_time

    

    # Creat list of friends who are not invited to an event
    already_invited_ids = [invitation.invitee_id for invitation in invitations]
    uninvited_friends = []
    # list of friend objs
    friends_of_creator = event_info.creator.friends

    for friend_of_creator in friends_of_creator:
        if friend_of_creator.user_id in already_invited_ids:
            continue
        uninvited_friends.append(friend_of_creator)


    return render_template('event_page.html', invitations=invitations, event_info=event_info, 
                           pictures=pictures, personal_invitation=personal_invitation, uninvited_friends=uninvited_friends)


@app.route('/invite-reply/<event_id>', methods=['POST'])
def invitations(event_id):
    """Replying to invititation."""

    invitation = Invitation.query.filter(Invitation.event_id == event_id).first()

    reply_str = request.form.get('reply')
    invitation.attending = reply_str == 'yes'

    invitation.notes = request.form.get('note')

    db.session.commit()

    return redirect('/event-page/{event_id}'.format(event_id=invitation.event_id))


@app.route('/upload-event-photos/<event_id>', methods=['POST'])
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

    # list of IDs
    invitees = request.form.getlist('friend')

    already_invited = Invitation.query.filter(Invitation.event_id == event_id,
                                         Invitation.invitee_id.in_(invitees)).all()

    already_invited_ids = [str(invitation.invitee_id) for invitation in already_invited]

    for invitee in invitees:
        if invitee in already_invited_ids:
            continue

        invitation = Invitation(
                                invitee_id=invitee,
                                event_id=event_id,
                                )

        db.session.add(invitation)
        db.session.commit()

        # send personalized text notification
        user = User.query.filter(User.user_id == invitee).first()
        event = Event.query.filter(Event.event_id == event_id).first()
        body="Hey {name}, you have an invite from {creator}!\nCheck it out at http://localhost:5000/event/{event_id}".format(
                                                                                                                             name=user.name,
                                                                                                                             creator=event.creator.name, 
                                                                                                                             event_id=event.event_id
                                                                                                                             )

        helpers.send_txt_notification(body)

    return redirect('/event-page/{event_id}'.format(event_id=event_id))


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
        return redirect('/')


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

    app.run(host="0.0.0.0")
