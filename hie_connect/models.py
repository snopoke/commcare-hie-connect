from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text
from hie_connect.util import to_dict

db = SQLAlchemy()


class Record(db.Model):
    __tablename__ = 'records'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    case_id = Column(String(64))
    user_id = Column(String(64))
    name = Column(String(255))
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
    
    def to_dict(self):
        r_dict = to_dict(self)
        r_dict['date'] = self.date.isoformat()
        return r_dict