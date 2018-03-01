import unittest

from server import app
from model import db, connect_to_db


class EventfullTests(unittest.TestCase):
    """Tests for my party site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get("/")
        self.assertIn("Eventfull", result.data)

    def test_logged_in(self):
        result = self.client.get("/")
        self.assertIn('Login', result.data)
        self.assertNotIn('Logout', result.data)
        

    def test_rsvp(self):
        result = self.client.post("/rsvp",
                                  data={"name": "Jane",
                                        "email": "jane@jane.com"},
                                  follow_redirects=True)
        self.assertNotIn('<h2>Please RSVP</h2>', result.data)
        self.assertIn('<h2>Party Details</h2>', result.data)


class EventfullDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///eventfull")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_games(self):
        """Test example data."""
        
        result = self.client.get("/games")
        self.assertIn('monopoly', result.data)


if __name__ == "__main__":
    unittest.main()
