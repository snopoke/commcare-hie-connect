from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text
db = SQLAlchemy()

class Record(db.Model):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    case = Column(Text)
    mhd = Column(Text)
    cda = Column(Text)
    response_code = Column(Integer)
    response_text = Column(Text)
    error = Column(Text)

    def __init__(self):
        self.date = datetime.utcnow()

    def __repr__(self):
        return '<Record %r>' % (self.id)