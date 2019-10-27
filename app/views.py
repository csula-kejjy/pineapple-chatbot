from .modules.chatbot.simple_chatbot import SimpleChatBot
from django.http import HttpResponse
from django.shortcuts import render
import boto3, sys

sys.path.insert(1, '/system')

from system.credentials import Credentials

cred = Credentials()
# Create your views here.

def app(request):
	return render(request, 'app/base.html', {})

def handle_message(request):

	if request.method == 'POST':

		bot = SimpleChatBot("Chad", user=cred.user, password=cred.password, database=cred.database_name)
		user_message = request.POST['user_message']
		
		input_dictionary = {'input': user_message}
		runtime_client = boto3.client("lex-runtime")

		lex_response = runtime_client.post_text(
					botName='CHANGE_ME',
					botAlias='CHANGE_ME',
					userId='CHANGE_ME',
					inputText=str(input_dictionary['input'])
				)

		dialogState = str(lex_response.get('dialogState', 'Could not get dialogState from lex response json'))

		# if the dialog state is 'ReadyForFulfillment'
	
		if dialogState == 'ReadyForFulfillment':

			# from lex's response, get the 'intentName' parameter, otherwise throw an error.
			intent = str(lex_response.get('intentName','Could not get intent.'))
		
			# from lex's response, get the 'slots' and 'name' parameters, otherwise throw an error.
			entity = str(lex_response.get('slots','Could not get slot.').get('Name','Could not get slot data.'))
			
			print('\n\n\n--\nYour intent is to: ' + intent)
			print('Your entity is: ' + entity + '\n--\n')

			# call bot's get_response() method, passing it the user's message, intent and entity
			bot_response = str(bot.get_response(input_dictionary["input"], intent, entity))

			print(bot_response)

		# if the dialog state is NOT 'ReadyForFulfillment'
		else:

			# call bot's get_link() method, passing it the user's message
			bot_response = str(bot.get_link(input_dictionary["input"]))
			print(bot_response)
			
	#self.wfile.write(bytes(bot_response, "utf8"))
	
	try:
		return HttpResponse(bot_response)
	except:
		lex_message = lex_response['message']
		return HttpResponse(lex_message)

	else:
		print('Request is not a POST method!')
		return HttpResponse('Non-POST response')

	return HttpResponse('No http method was made!')