from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import mysql.connector, sys

sys.path.insert(0, '..')

from system.credentials import Credentials

cred = Credentials()
file = 'calstatela4/crawledDict.txt'
db = mysql.connector.connect(user=cred.user, password=cred.password, database=cred.database_name)
cursor = db.cursor()
stopWords = set(stopwords.words('english'))

with open(file, "r", encoding='utf-8') as f:
    #query = "INSERT INTO links (keywords, url) VALUES (%s, %s)"

    query = "INSERT INTO crawler (term, url, keywords) VALUES (%s, %s, %s)"
    for line in f:
        regexLoc = line.find(": {")
        url = line[:regexLoc].strip()
        keywords = line[regexLoc+3:].strip()[:-1]
        keywords = keywords[:6000]
        k = keywords.replace('\"', '').replace('\'', '').replace(',', '')
        terms = word_tokenize(k)
        terms = [t for t in terms if t not in stopWords]
        for term in terms:
            cursor.execute(query, (term, url, keywords))

db.commit()