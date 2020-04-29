###		
#		IMPORTANT: This MUST be executed while in it's root directory.
#				..pineapple-chatbot\spider\>  
#		If you are NOT IN THIS DIRECTORY, YOU WILL GET ERRORS.
###

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import mysql.connector, sys, os.path, numpy as np, ast

# MySQL object access database
db = mysql.connector.connect(user='', password='', database='chatbot_dev')
cursor = db.cursor()

def populate():

	# file to be iterated through
	file = 'calstatela2/testing_set_data.txt'

	# query to populate the database
	query = "INSERT INTO crawler (url, keywords, category, subcategory) VALUES (%s, %s, %s, %s)"

	# set of word to be removed from an array of strings
	stopWords = set(stopwords.words('english'))

	with open(file, "r", encoding='utf-8') as f:
		for line in f:

			regexLoc = line.find(": {")
			#print(f"regexLoc: {regexLoc}\n")
			url = line[:regexLoc].strip()
			#print(f"url: {url}\n")
			keywords = line[regexLoc+3:].strip()[:-1]
			#print(f"keywords: {keywords}\n")
			keywords = keywords[:6000]
			#print(f"keywords: {keywords}\n")

			#k = keywords.replace('\"', '').replace('\'', '').replace(',', '')
			#terms = word_tokenize(k)
			#terms = [t for t in terms if t not in stopWords]
			#for term in terms:

			try:
				# if the url contains at least 2 directorys...
				cursor.execute(query, (url, keywords, url.split('/')[3], os.path.basename(url)))
			except:
				# if it does not, skip it for now...
				continue

	db.commit()

def generate_word_count():
	#exectue the query to get the keywords from url(s)
	query = ("""SELECT DISTINCT category FROM crawler""")
	cursor.execute(query)
	data = cursor.fetchall()
	categories = []
	for (word, ) in data:
		categories.append(word)

	urlDic = {}

	for category in categories:
		query = ("""SELECT keywords FROM crawler WHERE category = %s """)
		cursor.execute(query, (category, ))
		data = cursor.fetchall()

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
				dummy = item.replace("'", "").replace('"', "").replace("[", "").replace("]", "").replace(" ", '', 1).replace(":", "").replace("(", "").replace(")", "").replace('\\\\u200b', "")

				# if the phrase is numeric, only has one word, or the phrase's length is greater than 50
				if dummy.isnumeric() or len(dummy.split(' ')) <= 1:
					continue

				for w in dummy.split(" "):

					#Add the dummy into the dictionary
					if w not in wordDic:
						wordDic[w.lower()] = 1
						wordCountForCategory += 1
			
					# increments dummy count if seen before
					else:
						wordDic[w.lower()] += 1
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

		# print(urlDic)

	save_to_file(urlDic, "../app/modules/chatbot/data_word_count.txt")

def save_to_file(data, filename):
	f = open(filename, "w")
	f.write(str(data))
	f.close()

def main():

	populate()

	generate_word_count()

if __name__ == '__main__':
	main()