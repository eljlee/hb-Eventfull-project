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


	def __repr__(self):
		"""Provide helpful representation when printed"""

		return "< User user_id={} name={} email={} >".format(self.user_id, self.name, self.email)


class Event(db.Model):
	"""Event."""

	__tablename__ = "events"

	event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	title = db.Column(db.String(64), nullable=False)
	start_at = db.Column(db.DateTime, nullable=False)
	end_at = db.Column(db.DateTime, nullable=False)
	creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	public = db.Column(db.Boolean, nullable=True)

	user = db.relationship('User', backref=db.backref('events', order_by=event_id))

	
	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "< Event event_id={} title={} start_at={} end_at={} >".format(self.event_id, 
																			 self.title, 
																			 self.start_at, 
																			 self.end_at)


class Invitation(db.Model):
	"""Invitation."""

	#"wedding invitation"

	__tablename__ = "invitations"

	invitee_id = db.Column(db.Integer, primary_key=True)
	creator = db.Column(db.Integer, db.ForeignKey('users.user_id')) #invitor_id? event_creator
	event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
	attending = db.Column(db.Boolean, nullable=True)
	notes = db.Column(db.String(128), nullable=True)

	user = db.relationship('User', backref=db.backref('invitations', order_by=invitee_id))

	event = db.relationship('Event', backref=db.backref('invitations', order_by=invitee_id))


	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "< Invitation invitee_id={} creator={} event_id={} attending={} >".format(self.invitee_id, 
																						 self.creator, 
																						 self.event_id, 
																						 self.attending)


class Picture(db.Model):
	"""Posting picture."""

	__tablename__ = 'pictures'

	pic_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	filename = db.Column(db.String(64), nullable=False)
	uploader_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))

	user = db.relationship('User')

	# event = db.relationship('Event')


	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "< Picture pic_id={} filename={} uploader_id={} event_id={} >".format(self.pic_id, 
																					 self.filename, 
																					 self.uploader_id, 
																					 self.event_id)


class Friendship(db.Model):
	"""Friending."""

	__tablename__ = 'friendships'

	friendship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	friend_1 = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	friend_2 = db.Column(db.Integer, db.ForeignKey('users.user_id'))

	user = db.relationship('User')






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
