from datetime import datetime
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db
from app import login


@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class User(UserMixin, db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	
	annotations = db.relationship('Annotation', backref='user', lazy=True)
	stats = db.relationship('UserStats', backref='user', lazy=True)

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def n_finished_questions(self):
		finished_questions = self.stats
		return len(finished_questions)

	def get_avatar(self, size):
		email = '{}@gmail.com'.format(self.username)
		digest = md5(email.encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}d=identicon'.format(
            digest, size)


class Question(db.Model):
	__tablename__ = 'question'

	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.PickleType)
	
	answer = db.relationship('Answer', backref='answer', uselist=False, lazy=True)
	annotations = db.relationship('Annotation', backref='question', lazy=True)

	def __repr__(self):
		return '<Question {}>'.format(self.id)


class Answer(db.Model):
	__tablename__ = 'answer'

	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.PickleType)

	# foreign keys
	question_id = db.Column(db.Integer, db.ForeignKey('question.id')) 

	def __repr__(self):
		return '<Question {}>'.format(self.id)


class Annotation(db.Model):
	__tablename__ = 'annotation'

	id = db.Column(db.Integer, primary_key=True)
	
	# foreign keys
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	question_id = db.Column(db.Integer, db.ForeignKey('question.id'))	

	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	content = db.Column(db.Text)

	def __repr__(self):
		return '<Annotation {} for Q{}>'.format(self.id, self.question_id)


class UserStats(db.Model):
	__tablename__ = 'userstats'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	# keep track of the all the finished questions
	finished_question_id = db.Column(db.Integer)

	def __repr__(self):
		return '<UserStats {}>'.format(self.id)