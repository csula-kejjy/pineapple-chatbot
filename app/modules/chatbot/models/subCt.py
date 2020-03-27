import mysql.connector
import os

#connect to mysql database
mydb = mysql.connector.connect(
	host = "",
	user = "",
	password="",
	database=""
)

#initiate database object
myCursor = mydb.cursor()

#exectue the query to get the urls
command = ("select url, keywords from crawler where url like '%faculty/%'")
myCursor.execute(command)
myResults = myCursor.fetchall()

labels = [] #list of labels
myString = '' #a string that will be tranformed to training data
dStrings = [] #list of modified strings from myString - ready training data
tStrings = [] #a list of dStrings list
trainingData= []
counter = 0
for url in myResults:
	
	#grab the faculty label
	dummy = url[0].split('/')
	dummy = dummy[4]
	labels.append(dummy)

	#Take the "keywords" string and make it a list
	myString = url[1]
	myString = list(myString.split(','))

	for s in myString:
		if len(s) < 50:
			dummy = s.replace("\'", '').replace('\"', '')
			
			if dummy[0] == ' ':
				dummy = dummy.replace(' ', '', 1)
			dStrings.append(dummy)
	
	tStrings.append(dStrings)
	dStrings = []
	counter += 1
	if counter == 2:
		break
myCursor.close()
print(len(tStrings), len(labels))

##########################################
path = 'C:\\Users\\jakre\\OneDrive\\Desktop\\chatBotHelpers\\trash'
#create folder
try:
    os.mkdir(path)
except OSError as error:
    {}

#create file and see training data
f = open(path + "\\gomi2.txt", 'w')
f.close()

f = open(path + "\\gomi2.txt", 'a', encoding='utf-8')

for i in range(len(labels)):
	f.write(labels[i] + "\n")
	for j in tStrings[i]:
		tSet = (j, {'entities':[(0, len(j), labels[i])]})
		f.write(str(tSet) + "\n")

f.close()


# for l, s in zip(labels, tStrings):
# 	print(l, ": ", s)
# 	print()


# for s in tStrings:
# 	print(len(s))
# 	for i in s:
# 		print(i)
# 	print()
# 	print()
# print(dummy, "is length:", len(dummy))
# myCursor.close()

# a = 'http://www.calstatela.edu/faculty/abbas-daneshvari'
# b = a.split("/")
# b = b[4].replace('-', ' ')
# print(b)