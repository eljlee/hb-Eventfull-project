###### model file - create tables ##### 
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##### Model definitions #####

class User(db.Model):
    """Users."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False, unique=True)
    phone = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(256), nullable=True)

    friends = db.relationship('User', secondary='friendships',
                              primaryjoin='User.user_id==Friendship.friend_1_id',
                              secondaryjoin='User.user_id==Friendship.friend_2_id')

    #must add friendship twice, one way, then the other


    def __repr__(self):
        """Provide helpful representation when printed"""

        return "< User user_id={} name={} email={} >".format(self.user_id, self.name, self.email)


class Event(db.Model):
    """Event."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    location = db.Column(db.String(128), nullable=True)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.String(64), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


    creator = db.relationship('User', backref=db.backref('created_events'))

    invitees = db.relationship('User', secondary='invitations', backref='invited_events')
    #go first to inivation class to get user_id, then go to users

    
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "< Event event_id={} title={} location={} start_at={} end_at={} note={} creator={}>".format(
                                                                                                           self.event_id, 
                                                                                                           self.title, 
                                                                                                           self.location,
                                                                                                           self.start_at, 
                                                                                                           self.end_at,
                                                                                                           self.note,
                                                                                                           self.creator_id
                                                                                                           )


class Invitation(db.Model):
    """Invitation."""

    __tablename__ = "invitations"

    invitation_id = db.Column(db.Integer, primary_key=True)
    invitee_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    attending = db.Column(db.Boolean, nullable=True)
    notes = db.Column(db.String(128), nullable=True)

    event = db.relationship('Event', backref='invitations')

    invitee = db.relationship('User', backref='invitations')


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "< Invitation invitation_id={} invitee_id={} event_id={} attending={} >".format(self.invitation_id,
                                                                                         self.invitee_id, 
                                                                                         self.event_id, 
                                                                                         self.attending
                                                                                         )


class Picture(db.Model):
    """Posting picture."""

    __tablename__ = 'pictures'

    pic_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    filename = db.Column(db.String(64), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))

    uploader = db.relationship('User')
    event = db.relationship('Event', backref='pictures')


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "< Picture pic_id={} filename={} uploader_id={} event_id={} >".format(self.pic_id, 
                                                                                     self.filename, 
                                                                                     self.uploader_id, 
                                                                                     self.event_id
                                                                                     )


class Friendship(db.Model):
    """Friending."""

    __tablename__ = 'friendships'

    friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend_1_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    friend_2_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # friend = db.relationship('User', backref='friendships')



#########################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///eventfull'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
