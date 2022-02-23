from datetime import datetime

from sqlalchemy.orm import validates
from mosp.bootstrap import db


class Event(db.Model):
    """Represent an event."""

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(), nullable=False)
    action = db.Column(db.String(), nullable=False)
    subject = db.Column(db.String(), nullable=False)
    initiator = db.Column(db.String())
    date = db.Column(db.DateTime(), default=datetime.utcnow)

    @validates("initiator")
    def validates_initiator(self, key: str, value: str):
        if any(bot in value for bot in ["SemrushBot", "AhrefsBot", "Googlebot"]):
            raise AssertionError("maximum length for email: 256")
        return value
