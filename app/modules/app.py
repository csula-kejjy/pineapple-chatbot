#from .chatbot.simple_chatbot import SimpleChatBot
import simplejson, boto3, pprint, sys
from io import BytesIO
import urllib.parse as urlparse

#bot = SimpleChatBot("Chad", user="enriq", password="P@ssword1", database="chatbot_dev")
runtime_client = boto3.client("lex-runtime")

def app(message):

	# creates a dictionary of the with the user's message {'input': message}
	input_dictionary = {'input': message}

	# call the Lex API with the user's message and get a response
	lex_response = runtime_client.post_text(
						botName='CSULA_ITS_CHATBOT',
						botAlias='CHATBOT_DEV',
						userId='01',
						inputText=str(input_dictionary['input'])
					)
	# from lex's response, get the dialog state parameter if it exists. Throw error it it cannot.
	dialogState = str(lex_response.get('dialogState', 'Could not get dialogState from lex response json'))

	## if the dialog state is 'ReadyForFulfillment'
	#if dialogState == 'ReadyForFulfillment':

	#	# from lex's response, get the 'intentName' parameter, otherwise throw an error.
	#	intent = str(lex_response.get('intentName','Could not get intent.'))
		
	#	# from lex's response, get the 'slots' and 'name' parameters, otherwise throw an error.
	#	entity = str(lex_response.get('slots','Could not get slot.').get('Name','Could not get slot data.'))
			
	#	print('\n\n\n--\nYour intent is to: ' + intent)
	#	print('Your entity is: ' + entity + '\n--\n')

	#	# call bot's get_response() method, passing it the user's message, intent and entity
	#	bot_response = str(bot.get_response(input_dictionary["input"], intent, entity))

	#	print(bot_response)

	## if the dialog state is NOT 'ReadyForFulfillment'
	#else:

	#	# call bot's get_link() method, passing it the user's message
	#	bot_response = str(bot.get_link(input_dictionary["input"]))
			
	#self.wfile.write(bytes(bot_response, "utf8"))
		
	#return bytes(bot_response, "utf8")

	return lex_response