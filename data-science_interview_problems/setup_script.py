import subprocess
import os
import pickle

from app.models import Question as db_Question
from app.models import Answer as db_Answer
from app import db
from questions import Question, Answer

# setup environment variables for flask application
os.environ['FLASK_APP'] = 'main.py'

def run_command(command):
	try:
		output = subprocess.check_output(
		    command,
		    shell=False,
		    stderr=subprocess.STDOUT,
		)
	except subprocess.CalledProcessError as err:
	    print('ERROR:', err)
	else:
		print(output.decode('utf8'))


# initiate flask database
if not os.path.exists('./app.db'):
	run_command('flask db init')
	run_command("flask db migrate")
	run_command('flask db upgrade')


# load existing question and answers to the database
existing_ids = [q.id for q in db_Question.query.all()]

with open('./questions/data/数据应用学院每日一题.pkl', 'rb') as f:
	content = pickle.load(f)

for obj in content:
	if obj.id in existing_ids:
		continue

	if obj.__class__.__name__ == 'Question':
		db.session.add(db_Question(id=obj.id, content=obj))
	else:
		db.session.add(db_Answer(id=obj.id, content=obj))
	db.session.commit()

