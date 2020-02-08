from difflib import SequenceMatcher
import mysql.connector as mc, pandas as pd, \
	os.path, Levenshtein as lev


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

		self.cursor.execute(query, ('%' + entity + '%', ))
		data = set(self.cursor.fetchall())

		#print(f'\n{data}\n')

		#print(len(data))

		# generate a DataFrame with three columns url, keywords, and score
		data_df = self.generate_dataframe_with_scores(data, entity)

		# sort the values from highest to lowest based on the 'score' column
		data_df = data_df.sort_values(by=['score'], ascending=False)

		print(f'\n{data_df}\n')
		return data_df

	def get_urls(self, tokens):
		result = []
		#print("tokens in get urls 2:", tokens)

		#query each token to the database and return a set of urls and keywords
		for t in tokens:
			command = "select distinct url, keywords from crawler where keywords like " + "'%" + t + "%'"
			print(f"\n{command}\n")
			self.cursor.execute(command)
			r = self.cursor.fetchall()
			print(len(r), " results for", t)

			# append r if items returned from query
			if r:
				result.append(set(r))

		if not result:
			return set()

		if len(result) > 0:
			data = result[0].intersection(*result[1:])

			# create a data frame with the data and tokens
			result_df = self.generate_dataframe_with_scores2(data, tokens)
			print(f'\n{result_df}\n')
			return result_df.iloc[0]['url']

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
			#print(text)
			data_df = data_df.append(
					{
					 'url': url, 
					 'keywords': text, 
					 'score': round(self.scoring_algorithm(os.path.basename(url), entity), 3)
					 },
					ignore_index=True)

		return data_df

	def generate_dataframe_with_scores2(self, data, tokens):

		data_df = pd.DataFrame(columns=["url","keywords","score"])
		for t in tokens:
			#print("Genereating for token:", t)
			for (url,keywords) in data:
				text = ""
				for word in keywords:
					text += word
					
				text = text.replace("'", "").replace(",", "")
				#print(text)
				data_df = data_df.append(
					{
						'url': url,
						'keywords': text,
						'score': round(lev.jaro(os.path.basename(url), t), 3)*1000
					}, ignore_index=True)
		data_df = data_df.sort_values(by=['score'], ascending=False)
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

	def scoring_algorithm(self, x, y):

		score_jaro = lev.jaro(x, y) 
		score_matcher = SequenceMatcher(None, x, y).ratio()

		return ((score_jaro + score_matcher) / 2)
		