import mysql.connector
import os
import spacy
import random
from pathlib import Path

#create a blank model
def create_model(cursor, td):
	nlp = spacy.blank('en')

	# create ner in the blank model
	ner = nlp.create_pipe('ner')
	nlp.add_pipe(ner)

	query = (""" SELECT DISTINCT category FROM crawler """)
	cursor.execute(query)
	data = set(cursor.fetchall())

	# add the labels into the blank model
	for (category, ) in data:
		ner.add_label(category.upper())

	#initialize the training
	nlp.begin_training()

	#train
	for i in range(10):
		#shuffle training data
		random.shuffle(td)
		losses = {}

		#batch examples and iterate through them
		for batch in spacy.util.minibatch(td, size = 2):

			#split the batch into text and annotations
			texts = [text for text, entities in batch]
			annoataions = [entities for text, entities in batch]

			nlp.update(texts, annoataions, losses = losses)
			print(losses)

	#save model
	output_dir = "../FacultyModel/"
	new_model_name = "facultyModel"

	if output_dir is not None:
		output_dir = Path(output_dir)

		if not output_dir.exists():
			output_dir.mkdir()
	
		nlp.meta['name'] = new_model_name
		nlp.to_disk(output_dir)

#connect to mysql database
mydb = mysql.connector.connect(
	host = "localhost",
	user = "enriq",
	password="P@ssword1",
	database="chatbot_dev"
)

# path for file to be written, current directory...
path = os.getcwd()

# initiate database object
myCursor = mydb.cursor()

# exectue the query to get the keywords and categories
query = (""" SELECT keywords, category FROM crawler """)  # WHERE category = "faculty" 
myCursor.execute(query)
data = set(myCursor.fetchall())

query = (""" SELECT DISTINCT category FROM crawler """)
myCursor.execute(query)
categories = set(myCursor.fetchall())
categories_arr = []
for (category, ) in categories:
	categories_arr.append(category)

print(categories_arr)

#Declaration(s)
td = []

for (keywords, category) in data:

	l = keywords.split(',')

	for item in l:
		# replace single quotes, double quotes, and brackets in the current string
		item = item.replace("\'", "").replace("\"", "").replace("[", "").replace("]", "").replace(" ", '', 1)	 

		
		# if the string is numeric and it has more than one word or it's length is greater than 50
		if len(item) >= 50:
			continue

		if item.isnumeric() or len(item.split(' ')) <= 1:
			tuple_wrong = (item, {'entities':[]})
			if not tuple_wrong in td:
				td.append(tuple_wrong) 

			continue		
		

		# construct tuple
		tuple = (item, {'entities':[(0, len(item), category.upper())]})

		# make sure only unique data is added
		if not tuple in td:
			td.append(tuple) 
		else:
			continue

# create file and see training data
f = open(path + "\\training_data.txt", 'w')
f.close()

f = open(path + "\\training_data.txt", 'a', encoding='utf-8')
for i in td:
	f.write(str(i) + "\n")

f.close()

create_model(myCursor, td)
myCursor.close()

