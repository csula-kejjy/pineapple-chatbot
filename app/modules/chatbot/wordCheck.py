import mysql.connector, numpy as np, ast
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

#connect to mysql database
mydb = mysql.connector.connect(
	host="localhost",
	user="enriq",
	password="P@ssword1",
	database="chatbot_dev")

#initiate database object
myCursor = mydb.cursor()

def generate_word_count():
	#exectue the query to get the keywords from url(s)
	query = ("""SELECT DISTINCT category FROM crawler""")
	myCursor.execute(query)
	data = myCursor.fetchall()
	categories = []
	for (word, ) in data:
		categories.append(word)

	urlDic = {}

	for category in categories:
		query = ("""SELECT keywords FROM crawler WHERE category = %s """)
		myCursor.execute(query, (category, ))
		data = myCursor.fetchall()

		wordList = []
		counter = 0
		myList = []
		wordDic = {}
		wordCountForCategory = 0

		for (word, ) in data:

			# take the long string and make into an list of smaller strings
			wordList = list(word.split(','))

			# only work with string lengths less than 50
			for item in wordList:

				# set up a dummy string for appendning to a dictionary
				dummy = item.replace("'", "").replace('"', "").replace("[", "").replace("]", "").replace(" ", '', 1).replace(":", "").replace("(", "").replace(")", "")

				# if the phrase is numeric, only has one word, or the phrase's length is greater than 50
				if dummy.isnumeric() or len(dummy.split(' ')) <= 1 or len(dummy) >= 50:
					continue

				for w in dummy.split(" "):

					#Add the dummy into the dictionary
					if w not in wordDic:
						wordDic.update({w.lower(): 1})
						wordCountForCategory += 1
			
					# increments dummy count if seen before
					else:
						wordCount = wordDic.get(w)
						updateQue = {w : wordCount + 1}
						wordDic.update(updateQue)
						wordCountForCategory += 1

			# used for testing small cases
			counter += 1
			if counter >= 2:
				break

		urlDic.update( {
						category.upper():
							(wordDic, wordCountForCategory)
						}
					 )

		print(urlDic)

	save_to_file(urlDic, "dict.txt")

def bayesian_naive_logic(question):

	# get a user's question

	# filter out the stopwords, keep only keywords
	stopWords = set(stopwords.words('english'))

	# tokenize the users input
	tokens = [i for i in word_tokenize(question) if i.lower() not in stopWords]
	print(f"\nTokenizing the user's input...\n\n\t{question} -> {tokens}")

	# remove "'"
	for t in tokens:
		if "'" in t or "?" in t or "!" in t:
			tokens.remove(t)
	print(f"\nRemoving symbols from tokens...\n\n\t -> {tokens}")

	# remove dr. from strings
	tokens = [t.replace("dr.", "") for t in tokens]
	print(f"\nRemoving pre-fixes from tokens...\n\n\t -> {tokens}")

	# get categories from db
	query = ("""SELECT DISTINCT category FROM crawler""")
	myCursor.execute(query)
	data = myCursor.fetchall()
	categories = []
	for (word, ) in data:
		categories.append(word)

	# keep an array with n number of elements (equal to 0)
	scores = [1 for i in range(len(categories))] 

	# read dictionary from file
	dict = read_from_file('dict.txt')

	# for each keyword and category
	for keyword in tokens:

		for item in dict:
			k, i = dict[item]
			if keyword in k:
				ratio = k[keyword]/i
				scores[categories.index(item.lower())] *= ratio
			else:
				scores[categories.index(item.lower())] *= 0.000099
	
	print('\n')			
	print(scores)
	print(categories)
	print(f'\n{max(scores)}')
	print(categories[scores.index(max(scores))])

def save_to_file(data, filename):
	f = open(filename, "w")
	f.write(str(data))
	f.close()

def read_from_file(filename):
	with open(filename, 'r') as f:
		s = f.read()
		data = ast.literal_eval(s)

	return data

def main():

	questions = ['Where is the student service center?']

	for question in questions:
		bayesian_naive_logic(question)

if __name__ == '__main__':
	main()


# if the word is bold, a title, subtitle, etc, give it add it 1,2,3,4... etc.
# get data which where we have questions that we know the answer too
# FOR THE FUTURE: while scoring all the links, the links with the category we found get a bonus added/multipied to it.