from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Admin(db.Model):
    __tablename__ = 'admins'
    id             = db.Column(db.Integer, primary_key=True)
    full_name      = db.Column(db.String(200), nullable=False)
    email          = db.Column(db.String(200), unique=True, nullable=False)
    password_hash  = db.Column(db.String(300), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    opportunities  = db.relationship('Opportunity',        backref='admin', lazy=True, cascade='all, delete-orphan')
    reset_tokens   = db.relationship('PasswordResetToken', backref='admin', lazy=True, cascade='all, delete-orphan')


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    id         = db.Column(db.Integer, primary_key=True)
    admin_id   = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    token      = db.Column(db.String(200), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used       = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id             = db.Column(db.Integer, primary_key=True)
    admin_id       = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    name           = db.Column(db.String(300), nullable=False)
    duration       = db.Column(db.String(100), nullable=False)
    start_date     = db.Column(db.String(50),  nullable=False)
    description    = db.Column(db.Text,        nullable=False)
    skills         = db.Column(db.Text,        nullable=False)
    category       = db.Column(db.String(100), nullable=False)
    future_opps    = db.Column(db.Text,        nullable=False)
    max_applicants = db.Column(db.String(50),  nullable=True)
    created_at     = db.Column(db.DateTime,    default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'name':           self.name,
            'duration':       self.duration,
            'start_date':     self.start_date,
            'description':    self.description,
            'skills':         self.skills,
            'category':       self.category,
            'future_opps':    self.future_opps,
            'max_applicants': self.max_applicants or '',
            'created_at':     self.created_at.isoformat()
        }
