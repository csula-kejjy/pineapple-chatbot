from django.http import HttpResponse
from django.shortcuts import render
from .modules.chatbot.simplechatbot import SimpleChatbot
import boto3, sys, speech_recognition as sr, time, spacy

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
			return HttpResponse('Something went wrong! Please try rephrasing your question.')

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
			print("\nMicrophone is active. Program is listening for your response...")

			r.adjust_for_ambient_noise(source)
			# listen to the microphone and save the recording
			audio = r.listen(source)

		# recognize speech using Google Speech Recognition
		try:

			# for testing purposes, we're just using the default API key
			# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			# instead of `r.recognize_google(audio)`
			
			print(f"\nGoogle Speech Recognition thinks you said: {r.recognize_google(audio)}")
			transcription = r.recognize_google(audio)
			return HttpResponse(transcription)

		except sr.UnknownValueError:
			print("\nGoogle Speech Recognition could not understand audio")
			return HttpResponse('\nGoogle Speech Recognition could not understand audio')
		except sr.RequestError as e:
			print(f"\nCould not request results from Google Speech Recognition service:\n {e}")
			return HttpResponse(e)

def call_lex(message):

	if not message: return "Please try asking me something next time... >:l"

	nlp = spacy.load("en_pineapple")
	
	ent_dic = {}

	for ent in nlp(message).ents:

		key = str(ent.label_) + ''
		if ent.label_ in ent_dic:
			ent_dic[key].append(str(ent)) if not str(ent) in ent_dic[key] else print(f'\nThe entity: {ent} is already in the array')
		else: 
			ent_dic[key] = [str(ent)]

	if 'email' in message:
		intent = 'GetEmail'
	elif 'phone' in message:
		intent = 'GetPhoneNumber'
	elif 'office' in message:
		intent = 'GetOfficeNumber'
	else:
		intent = None

	# summarize finds
	print(f"""\nUser input:\n\n\t-> {message}
			  \n\nIntent detected:\n\n\t-> {intent}
			  \n\nEntities detected:\n\n\t-> {ent_dic}""")

	# if no intent OR no entities were found...
	if not intent or not ent_dic:
		print("\nNo intent or entities were found. Calling get_link()...")
		return bot.get_link(message)
	# if BOTH a intent AND some entities were found...
	else:
		print(f"\nAn intent and a set of entities were found. Calling get_response()...")
		return bot.get_response(message, intent, ent_dic)