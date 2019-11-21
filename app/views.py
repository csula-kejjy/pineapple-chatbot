from django.http import HttpResponse
from django.shortcuts import render
from .modules.chatbot.simplechatbot import SimpleChatbot
import boto3, sys, speech_recognition as sr, time

sys.path.insert(1, '/system')

from system.credentials import Credentials

cred = Credentials()
# Create your views here.
bot = SimpleChatbot(user=cred.user, password=cred.password, database=cred.database_name)
runtime_client = boto3.client("lex-runtime")

def app(request):
	return render(request, 'app/base.html', {})

def handle_message(request):

	if request.method == 'POST':
			
		try:
			start_time = time.time()

			bot_response = call_lex(request.POST['user_message'])
			elapsed_time = time.time() - start_time
			print(f'\n\nTotal time elapsed: {elapsed_time}')
			return HttpResponse(bot_response)
		except Exception as e: 
			print(e)
			return HttpResponse('Cannot get response from Lex')

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

			r.adjust_for_ambient_noise(source)
			# listen to the microphone and save the recording
			audio = r.listen(source)

		# recognize speech using Google Speech Recognition
		try:

			# for testing purposes, we're just using the default API key
			# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			# instead of `r.recognize_google(audio)`

			print(f"Google Speech Recognition thinks you said: {r.recognize_google(audio)}")
			transcription = r.recognize_google(audio)
			return HttpResponse(transcription)

		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")
			return HttpResponse('Google Speech Recognition could not understand audio')
		except sr.RequestError as e:
			print(f"Could not request results from Google Speech Recognition service:\n {e}")
			return HttpResponse(e)

def call_lex(message):

	#if not message: return

	input_dictionary = {'input': message}

	lex_response = runtime_client.post_text(
				botName='CSULA_ITS_CHATBOT',
				botAlias='CHATBOT_DEV',
				userId='01',
				inputText=str(input_dictionary['input'])
			)

	print(f"\n\nLex's Response: {lex_response}\n\n")

	dialogState = str(lex_response.get('dialogState', 'Could not get dialogState from lex response json'))

	print(f"\n\nDialog State is: {dialogState}\n\n")
	# if the dialog state is 'ReadyForFulfillment'
	
	if dialogState == 'Fulfilled':

		# from lex's response, get the 'intentName' parameter, otherwise throw an error.
		intent = str(lex_response.get('intentName','Could not get intent.'))
		
		# from lex's response, get the 'slots' and 'name' parameters, otherwise throw an error.
		entity = str(lex_response.get('slots','Could not get slot.').get('professor_name','Could not get slot data.'))
			
		print('\n\n\n--\nYour intent is to: ' + intent)
		print('Your entity is: ' + entity + '\n--\n')

		# call bot's get_response() method, passing it the user's message, intent and entity
		bot_response = str(bot.get_response(input_dictionary["input"], intent, entity))

		print(f"\n\nSimpleChatbot's response: {bot_response}\n\n")
		
		return bot_response

	# if the dialog state is NOT 'ReadyForFulfillment'
	else:

		# call bot's get_link() method, passing it the user's message
		bot_response = str(bot.get_link(input_dictionary["input"]))
		print(bot_response)

		return bot_response

