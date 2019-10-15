from django.shortcuts import render
from django.http import HttpResponse
import boto3
# Create your views here.

def app(request):
	return render(request, 'app/header.html', {})

def handle_message(request):

	if request.method == 'POST':

		user_message = request.POST['user_message']
		
		input_dictionary = {'input': user_message}
		runtime_client = boto3.client("lex-runtime")

		lex_response = runtime_client.post_text(
					botName='CSULA_ITS_CHATBOT',
					botAlias='CHATBOT_DEV',
					userId='01',
					inputText=str(input_dictionary['input'])
				)

		print(lex_response)
		print(user_message)
		print(lex_response['message'])

		message = f"""
		<div class='btn btn-primary'>{user_message}</div>
		<div class='btn btn-primary'>{lex_response['message']}</div>
		"""

	else:
		print('Request is not a POST method!')

	return HttpResponse(message)