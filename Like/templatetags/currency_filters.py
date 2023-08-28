
from forex_python.converter import CurrencyRates
from django import template
from ipware import get_client_ip
import urllib
import json
import ipdata
import requests
from django.http import HttpResponse,JsonResponse

register = template.Library()

# class CurrencyMiddleware(View):
# 	def __init__(self, get_response):
# 		self.get_response = get_response

# 	def __call__(self, request):
# 		client_ip, _ = get_client_ip(request)
# 		print(client_ip,"hhhhhhhhh ip")
# 		if client_ip:
# 			# Determine user's location and preferred currency based on the IP
# 			# For simplicity, let's assume you have a function `get_location_and_currency`
# 			location, currency = get_location_and_currency(client_ip)

# 			# Store user's location and currency in session
# 			print(location," ip")
# 			print(currency,"currenc")
# 			request.session['user_location'] = location
# 			request.session['preferred_currency'] = currency

# 		response = self.get_response(request)
# 		return response
def convert_price(price, from_currency, to_currency):
	url = "https://openexchangerates.org/api/latest.json?app_id=0cb8570563234c40bd94b1321318e25a&&symbols="+to_currency+"&prettyprint=false&show_alternative=false"
	headers = {"accept": "application/json"}
	response = requests.get(url, headers=headers)
	# print(response.text)
	response_data = json.loads(response.text)
	data = response_data['rates']
	# Extract the exchange rate for NGN
	converted_price = list(data.values())[0]
	# if to_currency == 'NGN':
	# 	converted_price = response_data['rates']
	# 	print(converted_price,"kkkkkkkkkk")
	# else:
	# 	# print("Exchange rate for NGN:", converted_price)
	# 	converted_price = CurrencyRates().convert(from_currency, to_currency, price)
	print(converted_price)
	return converted_price


@register.filter(name='convert_to_user_currency')
def convert_to_user_currency(price,user_request):
	from_currency = "GBP"
	return convert_price_for_user(price, from_currency,user_request)

@register.simple_tag(takes_context=True)
def convert_price_for_user(price, from_currency, user_request):
	# request = context['request']
	request = user_request
	# client_ip, _ = get_client_ip(request)
	ipdata.api_key = "732979e1fb1072326c52f341ddda29a8fda0e18798bb7d71acfce533"
	client_ip = ipdata.lookup()
	if client_ip:
		# if _:
		# 	ip_type="public"
		# else:
		# 	ip_type="private"
		# # Determine user's location and preferred currency based on the IP
		# # For simplicity, let's assume you have a function `get_location_and_currency`
		# # ip_address = "105.113.35.109"
		# ip_address = "103.125.235.21"
		# auth = '8928e9d5-1aae-4d11-a0c9-b73890e895c6'
		# url = 'https://ipfind.co/?auth=' + auth + '&ip=' + ip_address
		# response = urllib.request.urlopen(url)
		# data = json.loads(response.read())
		# # url="https://api.ipfind.com/?ip="+ip_address
		# print(data)
		data = client_ip
		# print(data)
		location = data['country_name']
		currency = data['currency']['code']

		# Store user's location and currency in session
		request.session['user_location'] = location
		request.session['preferred_currency'] = currency
	else:
		client_ip="0.0.0.0"

	to_currency = request.session.get('preferred_currency', 'GBP')# Default to USD if not set
	returns = convert_price(price, from_currency, to_currency)
	return returns






#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@register.filter(name='convert_to_user_symbol')
def convert_to_user_symbol(price,user_request):
	from_currency = "GBP"
	return convert_symbol_for_user(price, from_currency,user_request)

@register.simple_tag(takes_context=True)
def convert_symbol_for_user(price, from_currency, user_request):
	# request = context['request']
	request = user_request
	# client_ip, _ = get_client_ip(request)
	ipdata.api_key = "732979e1fb1072326c52f341ddda29a8fda0e18798bb7d71acfce533"
	client_ip = ipdata.lookup()
	if client_ip:
		# if _:
		# 	ip_type="public"
		# else:
		# 	ip_type="private"
		# # Determine user's location and preferred currency based on the IP
		# # For simplicity, let's assume you have a function `get_location_and_currency`
		# # ip_address = "105.113.35.109"
		# ip_address = "103.125.235.21"
		# auth = '8928e9d5-1aae-4d11-a0c9-b73890e895c6'
		# url = 'https://ipfind.co/?auth=' + auth + '&ip=' + ip_address
		# response = urllib.request.urlopen(url)
		# data = json.loads(response.read())
		# # url="https://api.ipfind.com/?ip="+ip_address
		# print(data)
		data = client_ip
		location = data['country_name']
		currency = data['currency']['code']
		currency_symbol = data['currency']['symbol']
		# Store user's location and currency in session
		request.session['user_location'] = location
		request.session['preferred_currency'] = currency
		request.session['currency_symbol'] = currency_symbol
	else:
		client_ip="0.0.0.0"

	to_currency = request.session.get('currency_symbol', '£')# Default to USD if not set
	# c = CurrencyRates()
	# converted_symbol = c.convert(from_currency, to_currency, price)
	return to_currency

