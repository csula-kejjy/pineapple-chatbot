﻿from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from difflib import SequenceMatcher
from .mysqlstorage import MySQLStorage
import mysql.connector as mc, re, spacy
import pandas as pd

class SimpleChatbot:
	"""
	Build an object capable of interpreting a user's request with an answer
	"""

	def __init__(self, **kwargs):
		"""
		Build an object capable of interpreting a user's request with an answer
		"""
		self.storage = MySQLStorage(**kwargs)

		self.nlp = spacy.load('en_pineapple')

	def get_link(self, user_input):
		"""
		Return the a link or set of links based on the user's input.
		:param user_input: the user's input received
		:type user_input: str
		"""
		
	def get_response(self, user_input, intent, entity):
		"""
		Return a direct answer to the user's request.
		:param user_input: the user's input received
		:type user_input: str
		:param intent: an intent derived from the user's input which orginates from Amazon's Lex services
		:type intent: str
		:param entity: an entity derived from the user's input which orginates from Amazon's Lex services
		:type entity: str
		"""
		if not entity:
			return f"No entity was received from Amazon Lex services!"

		# Split the entity at every ' ' character
		# i.e 'this is some entity' -> ['this', 'is', 'some', 'entity']
		entity = entity.split(" ")

		print(f'\nQuerying the database...\n\tintent: {intent}\n\tentity: {entity}')

		# query the database based on the intent and the last element word from the entity array
		database_df = self.storage.query(intent, entity[-1])

		print(f'\nResponse from database saved...')

		if intent == 'GetEmail':
			print(f'\nFinding three closest emails that match: {entity[-1]}')
			emails = self.getEmail(database_df)
			return self.get_closest_email(emails, entity[-1])

		print(f'\nGenerating dictionary of entites...')
		#print(f'\nDictionary of Entities: {direct_answer}')

	def getEmail(self, data):
		"""
		Parse through a dataframe that contains a column of keywords for emails and return a array of unique emails found throughout the column. Keywords is a single string.
		:param data: a dataframe which must contain a column named keywords. Keywords is a single string.
		:type data: str
		"""

		# Empty array to hold unique emails
		no_dp_email = []

		# Loop through each row in the dataframe...
		for row in data.itertuples():

			# Parse through the row's keywords string for emails...
			emails = re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", row.keywords)

			# For each email in the array...
			for email in emails:
				email = str(email)

				# Append this email onto the array if it is not a repeat
				if email not in no_dp_email:
					no_dp_email.append(email)
		
		# return array of unique emails
		return no_dp_email

	def get_closest_email(self, emails, entity): 
		"""
		Compares and scores each email in a array with the entity provided by Amazon Lex. Returns a string which contains three emails that best match the entity. 
		:params emails: a array of emails returned by get_emails()
		:type emails: array
		:param entity: an entity derived from the user's input which orginates from Amazon's Lex services
		:type entity: str
		"""	

		# Creating an empty Dataframe with column names only
		df = pd.DataFrame(columns=['entity', 'score'])

		# Loop through each email...
		for email in emails:

			# Append a new row at the bottom: (email, comparison between this email and the entity provided)
			df = df.append(
					{
						'entity': email,
						'score': round(SequenceMatcher(None, email, entity).ratio(), 3)*1000
					},
					ignore_index=True)

		# Sort the dataframe by highest to lowest score
		df = df.sort_values(by=['score'], ascending=False)
		
		# Concatinate a string with the top 3 scoring emails
		answer = f"\nHere are a few possible answers:\n{df.iloc[0]['entity']},\n{df.iloc[1]['entity']},\n{df.iloc[2]['entity']}"

		# return the answer
		return answer

	def generate_entities(self, data):
		"""
		Generate a dictionary of entities using spaCy's NLP model. data MUST be in a dataframe which contains a columns labeled 'keywords'. Keywords is a single string.
		:param data: a dataframe that MUST have a column labeled 'keywords'. Keywords is a single string.
		:type data: DataFrame
		"""
		# create an empty dictionary to hold entities
		ent_dic = {}

		for row in data.itertuples():
			# feed nlp the first line's set of keywords
			doc = self.nlp(row.keywords)	
			# begin iterating through the nlp's entities
			for ent in doc.ents:

				# For each entity, check if the label exists in 'ent_dic'.
				# If it does, append the entity into the key, value pair.
				# If it doesn't, create a new key, value pair
				key = str(ent.label_) + ''
				if ent.label_ in ent_dic:
					ent_dic[key].append(str(ent)) if not str(ent) in ent_dic[key] else print(f'The entity: {ent} is already in the array')
				else: 
					ent_dic[key] = [str(ent)]

		# return the dictionary of entities
		return ent_dic

	####################################
	### FROM OLD simple_chatbot FILE ###
	####################################

	def compare(self, first_statement, second_statement):

		statement = first_statement.lower()

		other_statement = second_statement.lower()

		similarity = SequenceMatcher(None, statement, other_statement)

		return round(similarity.ratio(), 10)

	def shortest_link(self, response_set):

		def url_len(tup):
			return len(tup[0])

		return min(response_set, key=url_len)[0]

	def jaccard_sim_comparison(self, filtered_tokens, response_set):
		best_val = -1
		best_match = None

		for r in response_set:

			keywords = set(word_tokenize(
				r[1].replace('\'', '').replace(',', '')))

			tokens = set(filtered_tokens)

			val = len(tokens) / float(len(keywords))

			if val > best_val:
				best_val = val
				best_match = r[0]

		return best_match

	def closes_match2(self, filtered_tokens, response_set):
		best_val = -1
		best_match = None

		for r in response_set:
			val = 0

			path_start = r[0].find('.edu/') + 5
			path = r[0][path_start:]
			subdirs = path.split('/')

			for f in filtered_tokens:
				i = 1
				for s in subdirs:
					val += self.compare(f, r[0]) * i
					i *= 0.25

			val /= len(subdirs)

			if val > best_val:
				best_val = val
				best_match = r[0]

		return best_match

	def closest_match(self, filtered_tokens, response_list):
		best_val = 0
		best_match = None

		for r in response_list:
			keywords = r[1].replace('\"', '\'').split(',')

			path = r[2][r[2].find('.edu/')+5:]

			subdirs = path.split('/')

			kval = 0
			uval = 0
			sval = 0

			for f in filtered_tokens:
				for k in keywords:
					kval += self.compare(f, k)

				for u in subdirs:
					uval += self.compare(f, u)

			filtered_sent = ' '.join(filtered_tokens)

			for k in keywords:
				sval += self.compare(filtered_sent, k)

			kval /= len(keywords) * len(filtered_tokens)
			uval /= len(subdirs) * len(filtered_tokens)
			sval /= len(keywords)

			val = kval*0.25 + uval*0.25 + sval*0.5

			if val > best_val:
				best_val = val
				best_match = r[2]

		return best_match

	###################################
	### FROM OLD dataExtractor FILE ###
	###################################

	def remove_leading_spaces(self, text):
		while text[0] == ' ':
			text = text[1:]

		return text

	def get_entities(self, doc, intent):
		out = []

		for ent in doc.ents:

			if str(ent.label_) == self.intent_dict[intent]:

				if str(ent.label_) in ['ROOM', 'PHONE']:
					if not re.search('[0-9]', ent.text):
						continue
			
				if str(ent.label_) == 'EMAIL':
					if not re.search('@', ent.text):
						continue
				
				print(f" Answer found: {ent.text}")

				out.append(ent.text)
		
		return out

	def find_name(self, text, slot):
		texts = text.split(' ')

		for t in texts:
			t = re.sub('[^a-zA-Z0-9]', '',t)
			#print(self.compare(t, slot))
			if self.compare(t, slot) > 0.95:
				return True

		return False

	def compare(self, a, b):
		if not a or not b:
			return 0

		a = a.lower()
		b = b.lower()

		similarity = SequenceMatcher(None, a, b)

		# Calculate a decimal percent of the similarity
		percent = round(similarity.ratio(), 2)

		return percent