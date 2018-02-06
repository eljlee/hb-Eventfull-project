##### seed file - insert info to tables #####
from sqlalchemy import func
from model import User, Event, Invitation, Picture, Friendship

from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
	


