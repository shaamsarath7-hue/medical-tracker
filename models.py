from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='staff')  # 'admin' or 'staff'

class Syringe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    syringe_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Available')
    patient_info = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    history = db.relationship('SyringeHistory', backref='syringe', lazy=True)

class SyringeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    syringe_id = db.Column(db.Integer, db.ForeignKey('syringe.id'), nullable=False)
    old_status = db.Column(db.String(50))
    new_status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))
