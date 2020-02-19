from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import mysql.connector, sys, os.path

# file to be iterated through
file = 'calstatela4/particalDict.txt'

# MySQL object access database
db = mysql.connector.connect(user='enriq', password='P@ssword1', database='chatbot_dev')
cursor = db.cursor()

# set of word to be removed from an array of strings
stopWords = set(stopwords.words('english'))

# query to populate the database
query = "INSERT INTO crawler (url, keywords, category, subcategory) VALUES (%s, %s, %s, %s)"

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
