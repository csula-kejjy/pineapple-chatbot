from nltk.tokenize import word_tokenize
import re
import spacy
from spacy.matcher import Matcher

#Initiate spacy
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

#page_url = 'http://www.calstatela.edu/ecst/cs/faculty'
# page_url = 'http://www.calstatela.edu/academic/biol/ftfaculty.php'
# page_url = 'http://www.calstatela.edu/faculty/navid-amini'
# page_url = 'http://www.calstatela.edu/faculty/mohammad-pourhomayoun'
#hugeString = Spider.get_keywords(page_url)

#strings = ""
#for i in hugeString:
#   strings += i + " "

# string form
#print(strings)


def getEmail(input):
	emails = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", input)
	no_dp_email = []
	for email in emails:
		email = str(email)
		if email not in no_dp_email:
			no_dp_email.append(email)

	# if u want in string
	# email_string = ''
	# for i in no_dp_email:
	#     email_string += i + " "

	# print(email_string)
	return no_dp_email

def getPhone(strings):
	# validate phone: xxx-xxx-xxxx, (xxx)xxx-xxxx
	regex = "\w{3}-\w{3}-\w{4}"
	regex2 = "\(\w{3}\)\w{3}-\w{4}"

	# All phone number in the list
	phones = re.findall('[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', strings)
	no_dp_phone = []
	for phone in phones:
		phone = str(phone)
		# if phone not in no_dp_phone:
		#     no_dp_phone.append(phone)

		if re.search(regex, phone):
			if phone not in no_dp_phone:
				no_dp_phone.append(phone)
		elif re.search(regex2, phone):
			if phone not in no_dp_phone:
				no_dp_phone.append(phone)

	# if u want in string
	# phone_string = ''
	# for i in no_dp_phone:
	#     phone_string += i + " "

	# print(phone_string)
	return no_dp_phone


def getRoom(strings):
	pattern1 = [{"SHAPE": "XXX"}, {"SHAPE": "ddd"}]
	pattern2 = [{"SHAPE": "X&X"}, {"SHAPE": "X-ddd"}]
	pattern3 = [{"SHAPE": "XX"}, {"SHAPE": "Xddd"}]
	pattern4 = [{"SHAPE": "xx"}, {"SHAPE": "xddd"}]
	pattern5 = [{"SHAPE": "x&x"}, {"SHAPE": "x-ddd"}]
	pattern6 = [{"SHAPE": "xxx"}, {"SHAPE": "dddX"}]
	pattern7 = [{"SHAPE": "XXX"}, {"SHAPE": "dddX"}]
	pattern8 = [{"SHAPE": "XXXX"}, {"SHAPE": "ddd"}]
	pattern9 = [{"SHAPE": "XXXX"}, {"SHAPE": "dddX"}]

	pattern10 = [{"SHAPE": "XXX"}, {"SHAPE": "X-dddX"}]
	pattern11 = [{"SHAPE": "XXX"}, {"SHAPE": "X-dddx"}]
	pattern12 = [{"SHAPE": "X&X"}, {"SHAPE": "X-dddX"}]
	pattern13 = [{"SHAPE": "X&X"}, {"SHAPE": "X-dddx"}]
	pattern14 = [{"SHAPE": "xx"}, {"SHAPE": "X-dddX"}]
	pattern15 = [{"SHAPE": "XX-"}, {"SHAPE": "dddX"}]
	pattern16 = [{"SHAPE": "XX"}, {"ORTH": "-"}, {"SHAPE": "Xddd"}]

	pattern17 = [{"SHAPE": "XX"}, {"SHAPE": "ddd"}]

	matcher.add("ROOM", None, pattern1, pattern2, pattern3, pattern4,
				pattern5, pattern6, pattern7, pattern8, pattern9,
				pattern10, pattern11, pattern12, pattern13, pattern14,
				pattern15, pattern16, pattern17)

	doc = nlp(strings)
	matches = matcher(doc)
	myRoom = []
	for match_id, start, end in matches:
		room = doc[start:end]
		r = str(room)
		myRoom.append(r)

	# if u want in string
	# room_string = ''
	# for i in myRoom:
	#     room_string += i + " "

	# print(room_string)
	return myRoom



def extract_email_phone_room(strings):
	email = getEmail(strings)
	phone = getPhone(strings)
	room = getRoom(strings)
	# print(email)
	# print(phone)
	# print(room)

	return {'EMAIL': email, 'PHONE': phone, 'ROOM': room}

#x = extract_email_phone_room(strings)
#print(x)