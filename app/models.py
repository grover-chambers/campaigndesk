from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db
import json

def utc_now():
    return datetime.now(timezone.utc)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    candidate_name = db.Column(db.String(200), nullable=False)
    candidate_photo = db.Column(db.String(500))
    party = db.Column(db.String(100), nullable=False)
    seat_level = db.Column(db.String(50), nullable=False)
    county = db.Column(db.String(100), nullable=False)
    constituency = db.Column(db.String(200))
    ward = db.Column(db.String(200))
    constituency_code = db.Column(db.String(20))
    county_code       = db.Column(db.String(20))
    slogan = db.Column(db.String(300))
    bio = db.Column(db.Text)
    manifesto = db.Column(db.Text)
    colors = db.Column(db.Text, default='{"primary": "#4A5568", "secondary": "#718096"}')
    website = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    whatsapp_connected = db.Column(db.Boolean, default=False)
    whatsapp_config = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    
    def get_colors(self):
        try:
            return json.loads(self.colors) if self.colors else {'primary': '#4A5568', 'secondary': '#718096'}
        except:
            return {'primary': '#4A5568', 'secondary': '#718096'}

class Member(db.Model, UserMixin):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(200))
    role = db.Column(db.String(50), default='member')
    role_display = db.Column(db.String(100))
    access_code = db.Column(db.String(10), nullable=False)
    profile_photo = db.Column(db.String(500))
    manager_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    ward = db.Column(db.String(100))
    village = db.Column(db.String(100))
    member_type = db.Column(db.String(20), default='supporter')  # official | supporter
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    campaign = db.relationship('Campaign', backref=db.backref('members', lazy='dynamic'))
    subordinates = db.relationship('Member', backref=db.backref('manager', remote_side=[id]))

    def get_id(self):
        return str(self.id)

class Bulletin(db.Model):
    __tablename__ = 'bulletins'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(30), default='update')
    is_public = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    scheduled_for = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    published_at = db.Column(db.DateTime, default=utc_now)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    campaign = db.relationship('Campaign', backref=db.backref('bulletins', lazy='dynamic'))
    author = db.relationship('Member', foreign_keys=[author_id])

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    venue = db.Column(db.String(200))
    ward = db.Column(db.String(100))
    coordinates = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=True)
    rsvp_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='scheduled')
    created_by = db.Column(db.Integer, db.ForeignKey('members.id'))
    event_type = db.Column(db.String(50), default='baraza')  # baraza | team_meeting | rally | press | fundraiser
    minutes_url = db.Column(db.String(500))
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    campaign = db.relationship('Campaign', backref=db.backref('events', lazy='dynamic'))
    creator = db.relationship('Member', foreign_keys=[created_by])

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(50), default='pending')
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now)
    
    campaign = db.relationship('Campaign', backref=db.backref('tasks', lazy='dynamic'))
    assignee = db.relationship('Member', foreign_keys=[assigned_to])
    assigner = db.relationship('Member', foreign_keys=[assigned_by])

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    donor_name = db.Column(db.String(200))
    donor_phone = db.Column(db.String(20))
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default='pending')
    received_by = db.Column(db.Integer, db.ForeignKey('members.id'))
    created_at = db.Column(db.DateTime, default=utc_now)

class WhatsAppMessage(db.Model):
    __tablename__ = 'whatsapp_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    recipient_phone = db.Column(db.String(20))
    recipient_group = db.Column(db.String(50))
    message_type = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utc_now)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    action_type = db.Column(db.String(50))
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utc_now)
    
    campaign = db.relationship('Campaign', backref=db.backref('activity_logs', lazy='dynamic'))
    member = db.relationship('Member', foreign_keys=[member_id])

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='admin')
    is_superadmin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def get_id(self):
        return str(self.id)


class Document(db.Model):
    __tablename__ = 'documents'

    id               = db.Column(db.Integer, primary_key=True)
    campaign_id      = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False)
    title            = db.Column(db.String(300), nullable=False)
    doc_type         = db.Column(db.String(30), default='document')  # minutes | photo | document | gallery | manifesto
    cloudinary_url   = db.Column(db.String(600), nullable=False)
    cloudinary_id    = db.Column(db.String(300))
    thumbnail_url    = db.Column(db.String(600))
    event_id         = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    is_public        = db.Column(db.Boolean, default=False)
    caption          = db.Column(db.String(300))
    uploaded_by      = db.Column(db.Integer, db.ForeignKey('members.id'))
    created_at       = db.Column(db.DateTime, default=utc_now)

    campaign = db.relationship('Campaign', backref=db.backref('documents', lazy='dynamic'))
    event    = db.relationship('Event', backref=db.backref('documents', lazy='dynamic'))


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id           = db.Column(db.Integer, primary_key=True)
    campaign_id  = db.Column(db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False, unique=True)
    tier         = db.Column(db.String(30), default='starter')   # starter | constituency | county
    status       = db.Column(db.String(20), default='trial')     # trial | active | overdue | cancelled
    trial_ends   = db.Column(db.DateTime)
    last_paid    = db.Column(db.DateTime)
    next_due     = db.Column(db.DateTime)
    mpesa_ref    = db.Column(db.String(100))
    amount_paid  = db.Column(db.Float, default=0)
    created_at   = db.Column(db.DateTime, default=utc_now)
    updated_at   = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    campaign = db.relationship('Campaign', backref=db.backref('subscription', uselist=False))

