from difflib import SequenceMatcher
import mysql.connector as mc
import pandas as pd
import os.path
import Levenshtein as SequenceMatcher

class MySQLStorage:
	"""
	Create a object to query a database and format the data into a DataFrame.
	"""
	def __init__(self, **kwargs):
		"""
		Initialzie a object that takes in the database's username, password, database name.
		:param **kwargs: database name, account username, and account password
		:type **kwargs: str, str, str
		"""
		user = kwargs.get('user', 'root')
		password = kwargs.get('password')
		database_name = kwargs.get('database')

		if password != None:
			self.database = mc.connect(
					user=user,
					password=password,
					database=database_name,
					auth_plugin='mysql_native_password'
				)
		else:
			self.database = mc.connect(
					user=user,
					database=database_name
				)

		self.cursor = self.database.cursor(buffered=True)

	def query(self, intent, entity):
		"""
		Returns a DataFrame based on the intent declared by Amazon's Lex
		:param intent: an intent derived from the user's input which orginates from Amazon's Lex services
		:type intent: str
		:param entity: an entity derived from the user's input which orginates from Amazon's Lex services
		:type entity: str
		"""

		# add '%' wildcard symbols to entity string
		entity = '%' + entity + '%'
		query = ("""
					SELECT DISTINCT
						url,
						keywords 
					FROM 
						crawler 
					WHERE 
						url LIKE '%http://www.calstatela.edu/faculty/%'
					AND 
						keywords LIKE %s
				""")
		self.cursor.execute(query, (entity, ))
		data = set(self.cursor.fetchall())

		#print(f'\n{data}\n')

		#print(len(data))


		# check which intent is declared and set the base query for that intent
		#if intent == 'GetEmail':
		#	query = ("""
		#				SELECT DISTINCT
		#					url,
		#					keywords 
		#				FROM 
		#					crawler 
		#				WHERE 
		#					term = 'email'
		#				or
		#					term = 'e-mail'
		#				AND 
		#					keywords LIKE %s
		#			""")
		#	self.cursor.execute(query, (entity,))

		#elif intent == "GetPhoneNumber":
		#	query = ("""
		#				SELECT DISTINCT
		#					url,
		#					keywords 
		#				FROM 
		#					crawler 
		#				WHERE 
		#					term = 'phone'
		#				AND 
		#					keywords LIKE %s
		#			""")
		#	self.cursor.execute(query, (entity,))

		#elif intent == "GetOfficeRoom":

		#	query = ("""
		#				SELECT DISTINCT
		#					url,
		#					keywords 
		#				FROM 
		#					crawler 
		#				WHERE 
		#					term = 'office'
		#				AND 
		#					keywords LIKE %s
		#			""")
		#	self.cursor.execute(query, (entity,))
				
		## execute query and save data onto variable
		#data = set(self.cursor.fetchall())

		#print(f'\n{data}\n')

		# remove wildcard '%' symbols from entity string
		entity = entity.replace('%', '')

		# generate a DataFrame with three columns url, keywords, and score
		data_df = self.generate_dataframe_with_scores(data, entity)

		# sort the values from highest to lowest based on the 'score' column
		data_df = data_df.sort_values(by=['score'], ascending=False)

		print(f'\n{data_df}\n')
		return data_df

	def get_urls2(self, tokens):	
		result = []

		for t in tokens:
			self.cursor.execute(self.base_query, (t,))
			r = self.cursor.fetchall()

			if r:
				result.append(set(r))

		if not result:
			return set()

		if len(result) > 1:
			return result[0].intersection(*result[1:])
		else:
			return result[0]

	def generate_dataframe_with_scores(self, data, entity):
		"""
		Return a DataFrame with the columns 'url', 'keywords', and 'score' and populate the score column
		:param data: a set of tuples ('url', 'keywords')
		:type data: tuple('url', 'keywords')
		:param entity: an entity derived from the user's input which orginates from Amazon's Lex services
		:type entity: str
		"""
		data_df = pd.DataFrame(columns=['url', 'keywords', 'score'])

		for (url, keywords) in data:
			# parse the dataset into a single clean string 
			text = ""
			for word in keywords:
				text += word
			text = text.replace("'", "").replace(",", "")
			print(text)
			#print(os.path.basename(url))
			data_df = data_df.append(
					{
					 'url': url, 
					 'keywords': text, 
					 'score': round(SequenceMatcher.jaro(os.path.basename(url), entity), 3)*1000
					 },
					ignore_index=True)

		return data_df

	def generate_dataframe_without_scores(self, data):
		"""
		Return a DataFrame with the columns 'url', 'keywords', and 'score'. Each score is defaulted to 0.
		:param data: a set of tuples ('url', 'keywords')
		:type data: tuple('url', 'keywords')
		"""
		data_df = pd.DataFrame(columns=['url', 'keywords', 'score'])

		for (url, keywords) in data:
			text = ""
			for word in keywords:
				text += word

			# parse the dataset into a single clean string 
			text = text.replace("'", "").replace(",", "")
			data_df = data_df.append(
					{
					 'url': url, 
					 'keywords': text, 
					 'score': 0
					 },
					ignore_index=True)

		return data_df


