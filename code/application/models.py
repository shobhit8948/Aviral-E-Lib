from application.database import db 
from datetime import datetime
from sqlalchemy.orm import relationship
book_buyers = db.Table(
    'book_buyers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('access_start_datetime', db.DateTime, nullable=False),
    db.Column('access_end_datetime', db.DateTime, nullable=False),
    db.Column('price', db.Float, nullable=False),
    db.Column('access_duration', db.Integer, nullable=False)
)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    purchased_books = relationship("Book", secondary=book_buyers, backref="users")

    def __init__(self, name, phone, email, password):
        self.name = name
        self.phone = phone
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'role': self.role
        }
class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False) 

    def __init__(self, section_name, date_created, description, image):
        self.section_name = section_name
        self.date_created = date_created
        self.description = description
        self.image = image

    def to_dict(self):
        return {
            'id': self.id,
            'section_name': self.section_name,
            'date_created': self.date_created,
            'description': self.description,
            'image': self.image
        }
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    pdf = db.Column(db.String(200), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('books', lazy=True))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    price_per_day = db.Column(db.Float, nullable=False) 
    def __init__(self, title, author, content, image, pdf, section_id, price_per_day):
        self.title = title
        self.author = author
        self.content = content
        self.image = image
        self.pdf = pdf
        self.section_id = section_id
        self.price_per_day = price_per_day

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'content': self.content,
            'image_url': self.image,
            'pdf_url': self.pdf,
            'section_id': self.section_id,
            'date_created': self.date_created,
            'price_per_day': self.price_per_day 
        }

class PurchaseRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('purchase_requests', lazy=True))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    book = db.relationship('Book', backref=db.backref('purchase_requests', lazy=True))
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') 
    request_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  

    def __init__(self, user_id, book_id, duration, price):
        self.user_id = user_id
        self.book_id = book_id
        self.duration = duration
        self.price = price