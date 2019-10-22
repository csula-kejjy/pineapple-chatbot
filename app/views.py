from .modules.chatbot.simple_chatbot import SimpleChatBot
from django.http import HttpResponse
from django.shortcuts import render
import boto3, sys, speech_recognition as sr

sys.path.insert(1, '/system')

from system.credentials import Credentials

cred = Credentials()
# Create your views here.

def app(request):
	return render(request, 'app/base.html', {})

def handle_message(request, transcription=None):

	if request.method == 'POST':

		bot = SimpleChatBot("Chad", user=cred.user, password=cred.password, database=cred.database_name)

		print(transcription)
		user_message = request.POST['user_message']
		
		input_dictionary = {'input': user_message}
		runtime_client = boto3.client("lex-runtime")

		lex_response = runtime_client.post_text(
					botName='CSULA_ITS_CHATBOT',
					botAlias='CHATBOT_DEV',
					userId='01',
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

def handle_listen(request):

	if request.method == 'POST':

		# obtain audio from the microphone

		# create our Recognizer, which will handle receving and transcribing speech-to-text
		r = sr.Recognizer()

		# with our microphone set as default...
		with sr.Microphone() as source:
			print("Say something!")

			# listen to the microphone and save the recording
			audio = r.listen(source)

		# recognize speech using Google Speech Recognition
		try:
			# for testing purposes, we're just using the default API key
			# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			# instead of `r.recognize_google(audio)`
			print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
			print(r.recognize_google(audio))
			#request.POST['user_message'] = r.recognize_google(audio)
			handle_message(request, r.recognize_google(audio))
		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))