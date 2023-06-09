from django.db.models import Count, Q, Max
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import *
from django.http import HttpResponse
from users.models import *
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from paypal.standard.forms import PayPalPaymentsForm
import uuid
import random
import string
import requests


import stripe
# import Paystack

# paystack.api_key = settings.PAYSTACK_SECRET_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	context = {
		'order':order,
		'items': Item.objects.all()
	}
	return render(request, "products.html", context)


class SearchView(View):
	def get(self, request, *args, **kwargs):
		queryset = Item.objects.all()
		query = request.GET.get('q')
		if query:
			queryset = queryset.filter(
				Q(title__icontains=query) |
				Q(description__icontains=query)
			).distinct()
		context = {
			'queryset': queryset
		}
		return render(request, 'search_results.html', context)


def search(request):
	queryset = Item.objects.all()
	query = request.GET.get('q')
	if query:
		queryset = queryset.filter(
			Q(title__icontains=query) |
			Q(description__icontains=query)
		).distinct()
	context = {
		'queryset': queryset
	}
	return render(request, 'search_results.html', context)


def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid


class CheckoutView(View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			form = CheckoutForm()
			context = {
				'form': form,
				'couponform': CouponForm(),
				'order': order,
				'DISPLAY_COUPON_FORM': True
			}

			shipping_address_qs = Address.objects.filter(
				user=self.request.user,
				address_type='S',
				default=True
			)
			if shipping_address_qs.exists():
				context.update(
					{'default_shipping_address': shipping_address_qs[0]})

			billing_address_qs = Address.objects.filter(
				user=self.request.user,
				address_type='B',
				default=True
			)
			if billing_address_qs.exists():
				context.update(
					{'default_billing_address': billing_address_qs[0]})

			return render(self.request, "checkout.html", context)
		except ObjectDoesNotExist:
			messages.info(self.request, "You do not have an active order")
			return redirect("core:checkout")

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():

				use_default_shipping = form.cleaned_data.get(
					'use_default_shipping')
				if use_default_shipping:
					print("Using the defualt shipping address")
					address_qs = Address.objects.filter(
						user=self.request.user,
						address_type='S',
						default=True
					)
					if address_qs.exists():
						shipping_address = address_qs[0]
						order.shipping_address = shipping_address
						order.save()
					else:
						messages.info(
							self.request, "No default shipping address available")
						return redirect('core:checkout')
				else:
					print("User is entering a new shipping address")
					shipping_address1 = form.cleaned_data.get(
						'shipping_address')
					shipping_address2 = form.cleaned_data.get(
						'shipping_address2')
					shipping_country = form.cleaned_data.get(
						'shipping_country')
					shipping_zip = form.cleaned_data.get('shipping_zip')

					if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
						shipping_address = Address(
							user=self.request.user,
							street_address=shipping_address1,
							apartment_address=shipping_address2,
							country=shipping_country,
							zip=shipping_zip,
							address_type='S'
						)
						shipping_address.save()

						order.shipping_address = shipping_address
						order.save()

						set_default_shipping = form.cleaned_data.get(
							'set_default_shipping')
						if set_default_shipping:
							shipping_address.default = True
							shipping_address.save()

					else:
						messages.info(
							self.request, "Please fill in the required shipping address fields")

				use_default_billing = form.cleaned_data.get(
					'use_default_billing')
				same_billing_address = form.cleaned_data.get(
					'same_billing_address')

				if same_billing_address:
					billing_address = shipping_address
					billing_address.pk = None
					billing_address.save()
					billing_address.address_type = 'B'
					billing_address.save()
					order.billing_address = billing_address
					order.save()

				elif use_default_billing:
					print("Using the defualt billing address")
					address_qs = Address.objects.filter(
						user=self.request.user,
						address_type='B',
						default=True
					)
					if address_qs.exists():
						billing_address = address_qs[0]
						order.billing_address = billing_address
						order.save()
					else:
						messages.info(
							self.request, "No default billing address available")
						return redirect('core:checkout')
				else:
					print("User is entering a new billing address")
					billing_address1 = form.cleaned_data.get(
						'billing_address')
					billing_address2 = form.cleaned_data.get(
						'billing_address2')
					billing_country = form.cleaned_data.get(
						'billing_country')
					billing_zip = form.cleaned_data.get('billing_zip')

					if is_valid_form([billing_address1, billing_country, billing_zip]):
						billing_address = Address(
							user=self.request.user,
							street_address=billing_address1,
							apartment_address=billing_address2,
							country=billing_country,
							zip=billing_zip,
							address_type='B'
						)
						billing_address.save()

						order.billing_address = billing_address
						order.save()

						set_default_billing = form.cleaned_data.get(
							'set_default_billing')
						if set_default_billing:
							billing_address.default = True
							billing_address.save()

					else:
						messages.info(
							self.request, "Please fill in the required billing address fields")

				payment_option = form.cleaned_data.get('payment_option')

				if payment_option == 'S':
					return redirect('core:payment', payment_option='Paystack')
				elif payment_option == 'P':
					return redirect('core:paypal_payment', payment_option='paypal')
				else:
					messages.warning(
						self.request, "Invalid payment option selected")
					return redirect('core:checkout')
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("core:order-summary")


class PaymentView(View):
	def get(self, *args, **kwargs):
		if request.user.is_authenticated:
			order = Order.objects.get(user=self.request.user, ordered=False)
		else:
			order = False
		if order.billing_address:
			context = {
				'order': order,
				'DISPLAY_COUPON_FORM': False,
				'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
			}
			userprofile = self.request.user.userprofile
			if userprofile.one_click_purchasing:
				# fetch the users card list
				cards = stripe.Customer.list_sources(
					userprofile.stripe_customer_id,
					limit=3,
					object='card'
				)
				card_list = cards['data']
				if len(card_list) > 0:
					# update the context with the default card
					context.update({
						'card': card_list[0]
					})
			return render(self.request, "payment.html", context)
		else:
			messages.warning(
				self.request, "You have not added a billing address")
			return redirect("core:checkout")

	def post(self, *args, **kwargs):
		order = Order.objects.get(user=self.request.user, ordered=False)
		form = PaymentForm(self.request.POST)
		userprofile = UserProfile.objects.get(user=self.request.user)
		
		if form.is_valid():
			token = form.cleaned_data.get('stripeToken')
			save = form.cleaned_data.get('save')
			use_default = form.cleaned_data.get('use_default')

			print("tjk",save,"token",token,"def",use_default)

			if save:
				if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
					customer = stripe.Customer.retrieve(
						userprofile.stripe_customer_id)
					customer.sources.create(source=token)

				else:
					customer = stripe.Customer.create(
						email=self.request.user.email,
					)
					customer.sources.create(source=token)
					userprofile.stripe_customer_id = customer['id']
					userprofile.one_click_purchasing = True
					userprofile.save()

			amount = int(order.get_total() * 100)

			try:

				if use_default or save:
					# charge the customer because we cannot charge the token more than once
					charge = stripe.Charge.create(
						amount=amount,  # cents
						currency="USD",
						source=token,
						customer=request.user.id
					)
				else:
					# charge once off on the token
					charge = stripe.Charge.create(
						amount=amount,  # cents
						currency="gpb",
						source=token
					)

				# create the payment
				payment = Payment()
				payment.stripe_charge_id = charge['id']
				payment.user = self.request.user
				payment.amount = order.get_total()
				payment.save()

				# assign the payment to the order

				order_items = order.items.all()
				order_items.update(ordered=True)
				for item in order_items:
					item.save()

				order.ordered = True
				order.payment = payment
				order.ref_code = create_ref_code()
				order.save()

				messages.success(self.request, "Your order was successful!")
				return redirect("/")

			except stripe.error.CardError as e:
				body = e.json_body
				err = body.get('error', {})
				messages.warning(self.request, f"{err.get('message')}")
				return redirect("/")

			except stripe.error.RateLimitError as e:
				# Too many requests made to the API too quickly
				messages.warning(self.request, "Rate limit error")
				return redirect("/")

			except stripe.error.InvalidRequestError as e:
				# Invalid parameters were supplied to Stripe's API
				print(e)
				messages.warning(self.request, "Invalid parameters")
				return redirect("/")

			except stripe.error.AuthenticationError as e:
				# Authentication with Stripe's API failed
				# (maybe you changed API keys recently)
				messages.warning(self.request, "Not authenticated")
				return redirect("/")

			except stripe.error.APIConnectionError as e:
				# Network communication with Stripe failed
				messages.warning(self.request, "Network error")
				return redirect("/")

			except stripe.error.StripeError as e:
				# Display a very generic error to the user, and maybe send
				# yourself an email
				messages.warning(
					self.request, "Something went wrong. You were not charged. Please try again.")
				return redirect("/")

			except Exception as e:
				# send an email to ourselves
				messages.warning(
					self.request, "A serious error occurred. We have been notifed.")
				return redirect("/")

		messages.warning(self.request, "Invalid data received")
		return redirect("/payment/stripe/")

@login_required
def PaypalPayment(request,payment_option,):
	
	if request.user.is_authenticated:
		order = Order.objects.get(user=request.user, ordered=False)
	else:
		order = False
	amount = order.get_total()
	
	
	context = {
		'order': order,
		'DISPLAY_COUPON_FORM': False,
		'amount':amount,
	}
	# host = request.get_host()
	
	# paypal_dic = {
	# 	'business':settings.PAYPAL_RECEIVER_EMAIL,
	# 	'amount': amount,
	# 	'item_name': 'first peince',
	# 	'invoice':str(uuid.uuid4()),
	# 	'currency_code':'USD',
	# 	'notify_url': 'http://{}{}'.format(host, reverse("paypal-ipn")),
	# 	'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
	# 	'cancel_return': 'http://{}{}'.format(host, reverse("core:payment-failed")),
	# }
	# print("this the ",paypal_dic)
	# paypal_payment_button = PayPalPaymentsForm(initial=paypal_dic)
	return render(request,"paypal-page.html",context)


def InvoicePayment(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=request.user, ordered=False)
	else:
		order = False
	orderid = request.POST.get('orderid')
	orderid = request.POST['orderid']
	try:
				# create the payment
		payment = Payment()
		payment.paypal_order_id = orderid
		payment.user = request.user
		payment.amount = order.get_total()
		payment.save()

				# assign the payment to the order

		order_items = order.items.all()
		order_items.update(ordered=True)
		for item in order_items:
			item.save()
		order.ordered = True
		order.payment = payment
		order.ref_code = create_ref_code()
		order.save()
		response = "Your order was successful!"
		return HttpResponse(response)
		messages.success(request, "Your order was successful!")
		# return redirect("/")

	except stripe.error.CardError as e:
		return redirect("/")
	
	amount = order.get_total()
	if order.billing_address:
		context = {
			'order': order,
			'DISPLAY_COUPON_FORM': False,
			'amount':amount,
		}
	else:
		messages.warning(request, "You have not added a billing address")
		return redirect("core:checkout")
	# host = request.get_host()
	
	# paypal_dic = {
	# 	'business':settings.PAYPAL_RECEIVER_EMAIL,
	# 	'amount': amount,
	# 	'item_name': 'first peince',
	# 	'invoice':str(uuid.uuid4()),
	# 	'currency_code':'USD',
	# 	'notify_url': 'http://{}{}'.format(host, reverse("paypal-ipn")),
	# 	'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
	# 	'cancel_return': 'http://{}{}'.format(host, reverse("core:payment-failed")),
	# }
	# print("this the ",paypal_dic)
	# paypal_payment_button = PayPalPaymentsForm(initial=paypal_dic)
	return render(request,"invoice-page.html",context)



def payment_completed_view(request):
	return render(request,"payment-completed.html")

def payment_failed_view(request):
	return render(request,"payment-failed.html")

# class HomeView(ListView):
#     model = Item
#     paginate_by = 10
#     template_name = "menu.html"

# def Event_detailsDetailView(request, pk):
#     post = get_object_or_404(Event, pk=pk)
#     photos = PostImage.objects.filter(post=post)
#     return render(request, 'event_details.html', {
#         'post':post,
#         'photos':photos
#     })
class HomeView(ListView):
	def get(self, request, *args, **kwargs):

		featured_post = Item.objects.all()[:6]
		latest = Item.objects.order_by('-timestamp')[0:6]
		context = {
			'latest':latest,
		}
		return render(request, 'menu.html', context)

class IndexView(View):
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			order = Order.objects.get(user=self.request.user, ordered=False)
		else:
			order = False
		featured_post = Item.objects.filter(futured=True).order_by('-timestamp')[:10]
		category = Main_Category.objects.all().order_by('-id')
		latest = Item.objects.filter(seasson='NEW ARRIVALS').order_by('-timestamp')[0:10]
		best_sell = Item.objects.filter(seasson='BEST SELLER').order_by('-timestamp')[0:10]
		most_popular = Item.objects.filter(seasson='MOST POPULAR').order_by('-timestamp')[0:10]
		men_cloth = Item.objects.filter(category__name="Men's Clothing").order_by('-timestamp')[0:2]
		men_cloth2 = Item.objects.filter(category__name="Men's Clothing").order_by('-timestamp')[2:4]
		men_cloth3 = Item.objects.filter(category__name="Men's Clothing").order_by('-timestamp')[4:6]
		men_cloth4 = Item.objects.filter(category__name="Men's Clothing").order_by('-timestamp')[6:8]

		women_cloth = Item.objects.filter(category__name="Women's Clothing").order_by('-timestamp')[0:2]
		women_cloth2 = Item.objects.filter(category__name="Women's Clothing").order_by('-timestamp')[2:4]
		women_cloth3 = Item.objects.filter(category__name="Women's Clothing").order_by('-timestamp')[4:6]
		women_cloth4 = Item.objects.filter(category__name="Women's Clothing").order_by('-timestamp')[6:8]

		ACCESSORIES = Item.objects.filter(category__name='ACCESSORIES & SHOES').order_by('-timestamp')[0:2]
		ACCESSORIES2 = Item.objects.filter(category__name='ACCESSORIES & SHOES').order_by('-timestamp')[2:4]
		ACCESSORIES3 = Item.objects.filter(category__name='ACCESSORIES & SHOES').order_by('-timestamp')[4:6]
		ACCESSORIES4 = Item.objects.filter(category__name='ACCESSORIES & SHOES').order_by('-timestamp')[6:8]

		
		top_brand1 = Top_Brands.objects.order_by('-timestamp')[0:2]
		top_brand2 = Top_Brands.objects.order_by('-timestamp')[2:4]
		top_brand3 = Top_Brands.objects.order_by('-timestamp')[4:6]
		top_brand4 = Top_Brands.objects.order_by('-timestamp')[6:8]
		top_brand5 = Top_Brands.objects.order_by('-timestamp')[8:10]
		top_brand6 = Top_Brands.objects.order_by('-timestamp')[10:12]

		category_icon = Main_Category.objects.all()[0:6]
		# print('this the men cloths there',ACCESSORIES)
		context = {
			'order':order,
			'men_cloth':men_cloth,
			'men_cloth2':men_cloth2,
			'men_cloth3':men_cloth3,
			'men_cloth4':men_cloth4,

			'ACCESSORIES':ACCESSORIES,
			'ACCESSORIES2':ACCESSORIES2,
			'ACCESSORIES3':ACCESSORIES3,
			'ACCESSORIES4':ACCESSORIES4,


			'women_cloth':women_cloth,
			'women_cloth2':women_cloth2,
			'women_cloth3':women_cloth3,
			'women_cloth4':women_cloth4,
			'best_sell':best_sell,
			'most_popular':most_popular,
			'category':category,
			'category_icon':category_icon,
			'latest': latest,
			'futureds': featured_post,

			
			'top_brand1':top_brand1,
			'top_brand2':top_brand2,
			'top_brand3':top_brand3,
			'top_brand4':top_brand4,
			'top_brand5':top_brand5,
			'top_brand6':top_brand6,
		}
		return render(request, 'index.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			context = {
				'object': order
			}
			return render(self.request, 'order_summary.html', context)
		except ObjectDoesNotExist:
			messages.warning(self.request, "You do not have an active order")
			return redirect("/")


# class ItemDetailView(DetailView):
	
#     model = Item
#     template_name = "product.html"
def ItemDetailView(request, pk):
	objects = get_object_or_404(Item, pk=pk)
	latest = Item.objects.filter(seasson='NEW ARRIVALS').order_by('-timestamp')[0:3]
	# object = Item.objects.filter(item=post)
	featured_post = Item.objects.filter(futured=True).order_by('-timestamp')[:3]
	context = {
		'object': objects,
		'latest': latest,
		'futureds': featured_post
	}
	return render(request, 'product.html', context)


@login_required
def add_to_cart(request, pk):
	item = get_object_or_404(Item, id=pk)
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		ordered=False
	)
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__id=item.id).exists():
			order_item.quantity += 1
			order_item.save()
			messages.info(request, "This item quantity was updated.")
			return redirect("core:order-summary")
		else:
			order.items.add(order_item)
			messages.info(request, "This item was added to your cart.")
			return redirect("core:order-summary")
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user=request.user, ordered_date=ordered_date)
		order.items.add(order_item)
		messages.info(request, "This item was added to your cart.")
		return redirect("core:order-summary")


# class PaymentView(View):
# 	def get(self, *args, **kwargs):
# 		order = Order.objects.get(user=self.request.user, ordered=False)
# 		if order.billing_address:
# 			context = {
# 				'order': order,
# 				'DISPLAY_COUPON_FORM': False
# 			}
# 			userprofile = self.request.user.userprofile
# 			if userprofile.one_click_purchasing:
# 				# fetch the users card list
# 				cards = stripe.Customer.list_sources(
# 					userprofile.stripe_customer_id,
# 					limit=3,
# 					object='card'
# 				)
# 				card_list = cards['data']
# 				if len(card_list) > 0:
# 					# update the context with the default card
# 					context.update({
# 						'card': card_list[0]
# 					})
# 			return render(self.request, "payment.html", context)
# 		else:
# 			messages.warning(
# 				self.request, "You have not added a billing address")
# 			return redirect("/checkout")

# 	def post(self, *args, **kwargs):
# 		order = Order.objects.get(user=self.request.user, ordered=False)
# 		form = PaymentForm(self.request.POST)
# 		userprofile = UserProfile.objects.get(user=self.request.user)
# 		if form.is_valid():
# 			token = form.cleaned_data.get('stripeToken')
# 			save = form.cleaned_data.get('save')
# 			use_default = form.cleaned_data.get('use_default')

# 			if save:
# 				if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
# 					customer = stripe.Customer.retrieve(
# 						userprofile.stripe_customer_id)
# 					customer.sources.create(source=token)

# 				else:
# 					customer = stripe.Customer.create(
# 						email=self.request.user.email,
# 					)
# 					customer.sources.create(source=token)
# 					userprofile.stripe_customer_id = customer['id']
# 					userprofile.one_click_purchasing = True
# 					userprofile.save()

# 			amount = int(order.get_total() * 100)
# 			print("this the paramiter request here",userprofile.stripe_customer_id)
# 			try:

# 				if use_default or save:
# 					# charge the customer because we cannot charge the token more than once
# 					charge = stripe.Charge.create(
# 						amount=amount,  # cents
# 						currency="gpb",
# 						customer=userprofile.stripe_customer_id
# 					)
# 					print("this the paramiter request here",userprofile.stripe_customer_id)
# 				else:
# 					# charge once off on the token
# 					charge = stripe.Charge.create(
# 						amount=amount,  # cents
# 						currency="gpb",
# 						source=token
# 					)

# 				# create the payment
# 				payment = Payment()
# 				payment.stripe_charge_id = charge['id']
# 				payment.user = self.request.user
# 				payment.amount = order.get_total()
# 				payment.save()

# 				# assign the payment to the order

# 				order_items = order.items.all()
# 				order_items.update(ordered=True)
# 				for item in order_items:
# 					item.save()

# 				order.ordered = True
# 				order.payment = payment
# 				order.ref_code = create_ref_code()
# 				order.save()

# 				messages.success(self.request, "Your order was successful!")
# 				return redirect("/")

# 			except stripe.error.CardError as e:
# 				body = e.json_body
# 				err = body.get('error', {})
# 				messages.warning(self.request, f"{err.get('message')}")
# 				return redirect("/")

# 			except stripe.error.RateLimitError as e:
# 				# Too many requests made to the API too quickly
# 				messages.warning(self.request, "Rate limit error")
# 				return redirect("/")

# 			except stripe.error.InvalidRequestError as e:
# 				# Invalid parameters were supplied to Stripe's API
# 				print("this the errro report here",e)
# 				messages.warning(self.request, "Invalid parameters")
# 				return redirect("/")

# 			except stripe.error.AuthenticationError as e:
# 				# Authentication with Stripe's API failed
# 				# (maybe you changed API keys recently)
# 				messages.warning(self.request, "Not authenticated")
# 				return redirect("/")

# 			except stripe.error.APIConnectionError as e:
# 				# Network communication with Stripe failed
# 				messages.warning(self.request, "Network error")
# 				return redirect("/")

# 			except stripe.error.StripeError as e:
# 				# Display a very generic error to the user, and maybe send
# 				# yourself an email
# 				messages.warning(
# 					self.request, "Something went wrong. You were not charged. Please try again.")
# 				return redirect("/")

# 			except Exception as e:
# 				# send an email to ourselves
# 				messages.warning(
# 					self.request, "A serious error occurred. We have been notifed.")
# 				return redirect("/")

# 		messages.warning(self.request, "Invalid data received")
# 		return redirect("/payment/stripe/")


# def PaymentView(request):
# 	plan = request.GET.get('sub_plane')
# 	fetch_membership = Membership.objects.filter(membership_type=plan).exists()
# 	if fetch_membership == False:
# 		return redirect('subscrib')
# 	membership = Membership.objects.get(membership_type=plan)


# 	price = float(membership.price)*100
# 	price = int(price)
# 	def init_payment(request):
# 		url = 'https://api.paystack.co/transaction/initialize'
# 		headers = {
# 			'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
# 			'Content-type' : 'application/json',
# 			'Accept': 'application/json',
# 			}
# 		datum = {
# 			"email": request.user.email,
# 			"amount": price
# 			}
# 		x = requests.post(url, data=json.dumps(datum), headers=headers)
# 		if x.status_code != 200:
# 			return str(x.status_code)

# 		result = x.json()
# 		return result
# 	initialized = init_payment(request)
# 	print(initialized)
# 	amount = price/100
# 	instance = PayHistory.objects.create(amount=amount, payment_for=membership, user=request.user, paystack_charge_id=initialized['data']['reference'], paystack_access_code=initialized['data']['access_code'])
# 	UserMembership.objects.filter(user=instance.user).update(reference_code=initialized['data']['reference'])
# 	link = initialized['data']['authorization_url']
# 	return HttpResponseRedirect(link)
# 	return render(request, 'Template/subscrib.html')


def call_back_url(request):
	reference = request.GET.get('reference')

	check_pay = PayHistory.objects.filter(paystack_charge_id=reference).exists()
	if check_pay == False:
		print('error')
	else:
		payment = PayHistory.objects.get(paystack_charge_id=reference)

		def verify_payment(request):
			url = 'https://api.paystack.co/transaction/verify/'+reference
			headers = {
				'Authorization': 'Bearer '+settings.PAYSTACK_SECRET_KEY,
				'Content-type' : 'application/json',
				'Accept': 'application/json',
				}
			datum = {
				"reference": payment.paystack_charge_id
				}
			x = requests.get(url, data=json.dumps(datum), headers=headers)
			if x.status_code != 200:
				return str(x.status_code)

			result = x.json()
			return result
	initialized = verify_payment(request)
	if initialized['data']['status'] == 'success':
		PayHistory.objects.filter(paystack_charge_id=initialized['data']['reference']).update(paid=True)
		new_payment = PayHistory.objects.get(paystack_charge_id=initialized['data']['reference'])
		instance = Membership.objects.get(id=new_payment.payment_for.id)
		sub = UserMembership.objects.filter(reference_code=initialized['data']['reference']).update(membership=instance)
		user_membership = UserMembership.objects.get(reference_code=initialized['data']['reference'])
		Subscription.objects.create(user_membership=user_membership,expires_in=dt.now().date() + timedelta(days=user_membership.membership.duration))
		return redirect('/subscribed')  
	return render(request, 'Template/payment.html') 

@login_required
def remove_from_cart(request, pk):
	item = get_object_or_404(Item, id=pk)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__id=item.id).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			order.items.remove(order_item)
			messages.info(request, "This item was removed from your cart.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("core:product", id=pk)
	else:
		messages.info(request, "You do not have an active order")
		return redirect("core:product", id=pk)


@login_required
def remove_single_item_from_cart(request, pk):
	item = get_object_or_404(Item, id=pk)
	order_qs = Order.objects.filter(
		user=request.user,
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		# check if the order item is in the order
		if order.items.filter(item__id=item.id).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False
			)[0]
			if order_item.quantity > 1:
				order_item.quantity -= 1
				order_item.save()
			else:
				order.items.remove(order_item)
			messages.info(request, "This item quantity was updated.")
			return redirect("core:order-summary")
		else:
			messages.info(request, "This item was not in your cart")
			return redirect("core:product", id=pk)
	else:
		messages.info(request, "You do not have an active order")
		return redirect("core:product", id=pk)


def get_coupon(request, code):
	try:
		coupon = Coupon.objects.get(code=code)
		return coupon
	except ObjectDoesNotExist:
		messages.info(request, "This coupon does not exist")
		return redirect("core:checkout")


class AddCouponView(View):
	def post(self, *args, **kwargs):
		form = CouponForm(self.request.POST or None)
		if form.is_valid():
			try:
				code = form.cleaned_data.get('code')
				order = Order.objects.get(
					user=self.request.user, ordered=False)
				order.coupon = get_coupon(self.request, code)
				order.save()
				messages.success(self.request, "Successfully added coupon")
				return redirect("core:checkout")
			except ObjectDoesNotExist:
				messages.info(self.request, "You do not have an active order")
				return redirect("core:checkout")


class RequestRefundView(View):
	def get(self, *args, **kwargs):
		form = RefundForm()
		context = {
			'form': form
		}
		return render(self.request, "request_refund.html", context)

	def post(self, *args, **kwargs):
		form = RefundForm(self.request.POST)
		if form.is_valid():
			ref_code = form.cleaned_data.get('ref_code')
			message = form.cleaned_data.get('message')
			email = form.cleaned_data.get('email')
			# edit the order
			try:
				order = Order.objects.get(ref_code=ref_code)
				order.refund_requested = True
				order.save()

				# store the refund
				refund = Refund()
				refund.order = order
				refund.reason = message
				refund.email = email
				refund.save()

				messages.info(self.request, "Your request was received.")
				return redirect("core:request-refund")

			except ObjectDoesNotExist:
				messages.info(self.request, "This order does not exist.")
				return redirect("core:request-refund")


@csrf_protect
def welcome_user(request):
	context = {}
	if 'min_price' in request.GET.keys():
		filter_price1 = request.GET.get('min_price')
		filter_price2 = request.GET.get('max_price')
		if filter_price1 == '':
			filter_price1 = 0
		if filter_price2 == '':
			filter_price2 = Item.objects.all().aggregate(Max('price'))
		my_products = Item.objects.filter(price__range=(
			filter_price1, filter_price2['price_max']))
		context = {"products": my_products}
	return render(request, "welcome-user.html", context)


def list_category(request, slug):
	categories = Category.objects.all()
	post = Item.objects.all()
	if slug:
		category = get_object_or_404(Category, slug=slug)
		post = post.filter(category=category)
	template = "category.html"
	context = {
		'categories': categories,
		'post': post,
		'category': category,
	}
	return render(request, template, context)


def about_us(request):
	return render(request,'about-us.html')

def contact(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	if request.method == "POST":
		name = request.POST.get("name")
		email = request.POST.get("email")
		phone = request.POST.get("phone")
		massage = request.POST.get("massage")
		instance = contactUs.objects.create(name=name, email=email, phone=phone,massage=massage)
		instance.save()
		template = render_to_string('users/signup_massage.html',{
			"email": email
		})
			
		send_mail('From chopilosbyslippery',
		template,
		settings.EMAIL_HOST_USER,
		[email],
		)
		messages.success(request, f'Email Sent Successfully !')
		# return redirect('/login')
	return render(request,'contact-us.html',{'order':order})

# @login_required
# def reservation(request):
# 	if request.method == "POST":
# 		name = request.POST.get("name")
# 		email = request.POST.get("email")
# 		phone = request.POST.get("phone")
# 		date = request.POST.get("date")
# 		time = request.POST.get("time")
# 		person = request.POST.get("person")
# 		massage = request.POST.get("massage")
# 		instance = Reservation.objects.create(user=request.user,name=name, email=email,date=date,time=time,person=person, phone=phone,massage=massage)
# 		instance.save()
# 		template = render_to_string('users/signup_massage.html',{
# 			"email": email
# 		})
			
# 		send_mail('From chopilosbyslippery',
# 		template,
# 		settings.EMAIL_HOST_USER,
# 		[email],
# 		)
# 		messages.success(request, f'Reservation Booked Successfully !')

# 	res = Reservation.objects.filter(user=request.user).order_by('-timestamp')[:2]
# 	return render(request,'reservation.html',{'res':res})

def shop(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=request.user, ordered=False)
	else:
		order = False
	shops = Item.objects.all().order_by('-timestamp')
	const = {
		'order':order,
		"shops":shops
	}
	return render(request,"shop.html",const)

def sell_here(request):
	return render(request,"sell_here.html")

@login_required
def ListItem(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	vendors_list = BOUTIQUE_REQUEST.objects.filter(user=request.user).order_by('-id')
	category_list = Category.objects.all().order_by('-id')
	subcategory_list = Sub_Category.objects.all().order_by('-id')
	if request.method == "POST":
		pod = Item()
		pod.user=UserProfile.objects.get(user=request.user)
		pod.title = request.POST.get("title")
		pod.price = request.POST.get("price")
		pod.discount_price =  request.POST.get("discount_price")
		pod.Boutique_name =  request.POST.get("Boutique_name")
		pod.category = request.POST.get("category")
		pod.sub_category = request.POST.get("sub_category")
		pod.overview = request.POST.get("overview")
		pod.description = request.POST.get("description")
		if len(request.FILES) != 0:
			pod.image = request.FILES["image"]
			pod.image2 = request.FILES["image2"]
		pod.save()
		messages.success(request, f'Request has been sent Successfully !')
		 
		template = render_to_string('emails/ITEM_ADDED_EMAIL_TEM.html',{
			# "email": email
			"email": 'francisdaniel140@gmail.com'
		})
			
		send_mail('From Like Wise',
		template,
		settings.EMAIL_HOST_USER,
		['francisdaniel140@gmail.com','likegroupinc@gmail.com'],
		)
		messages.success(request, f'Request has been sent Successfully !')
		return redirect('/successfully')
	return render(request, "dashboard/list-item.html",{"vendors_list":vendors_list,'order':order,"category_list":category_list,"subcategory_list":subcategory_list})

@login_required
def sell_form(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	if request.method == "POST":
		pod = BOUTIQUE_REQUEST()
		pod.user=request.user
		pod.Boutique_name = request.POST.get("Boutique_name")
		pod.items_to_sell = request.POST.get("items_to_sell")
		pod.number =  request.POST.get("number")
		pod.where_else_you_sell = request.POST.get("where_else_you_sell")
		pod.social_media =  request.POST.get("social_media")
		pod.about_your_business = request.POST.get("about_your_business")
		pod.hear_about_us = request.POST.get("hear_about_us")
		if len(request.FILES) != 0:
			pod.brand_logo = request.FILES["brand_logo"]
			pod.brand_banner = request.FILES["brand_banner"]
			pod.products_image1 = request.FILES["products_image1"]
			pod.products_image2 = request.FILES["products_image2"]
			pod.products_image3 = request.FILES["products_image3"]
			pod.products_image4 = request.FILES["products_image4"]
		pod.save()
		messages.success(request, f'Request has been sent Successfully !')
		 
		template = render_to_string('emails/BOUTIQUE_REQUEST_EMAIL_TEM.html',{
			# "email": email
			"email": 'francisdaniel140@gmail.com'
		})
			
		send_mail('From Like Wise',
		template,
		settings.EMAIL_HOST_USER,
		['francisdaniel140@gmail.com','likegroupinc@gmail.com'],
		)
		messages.success(request, f'Request has been sent Successfully !')
		return redirect('/successfully')
	return render(request,"sell_form.html",{'order':order})

def successfully(request):
	return render(request,"successful.html")

def how_to_sell(request):
    return render(request, 'how-to-sell.html')

def vendors(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	vendors_list = BOUTIQUE_REQUEST.objects.filter(approved=True).order_by('-id')
	vendors_count = BOUTIQUE_REQUEST.objects.filter(approved=True)
	# for i in vendors_count:
	#     n = i.user
	#     print(n.count())
	# single_count = vendors_count.filter(user=request.user).count()
	return render(request,"vendors.html",{'order':order,'vendors_list':vendors_list})

def VendorDetailView(request, pk):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	# print(objects)
	latest = Item.objects.filter(Boutique_name=objects).order_by('-timestamp')
	# print("this it",latest)

	# object = Item.objects.filter(item=post)order.items.filter(item__id=item.id).exists():
	featured_post = Item.objects.filter(futured=True).order_by('-timestamp')[:3]
	context = {
		'object': objects,
		'latest': latest,
		'order':order,
		'futureds': featured_post
	}
	return render(request, 'vendor_details.html', context)

def about_us(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=self.request.user, ordered=False)
	else:
		order = False
	counters = counter.objects.all()
	return render(request,"about-us.html",{'order':order,'counter':counters})


def contact(request):
	return render(request,"contact.html")

@login_required
def Dashboard_sells(request):

	BOUTIQUE_ = BOUTIQUE_REQUEST.objects.filter(user=request.user).filter(approved=True).order_by('-id')
	vendors_list = BOUTIQUE_[0:4]
	vendors_list2 = BOUTIQUE_[4:8]
	vendors_list3 = BOUTIQUE_[8:12]
	context = {
		"vendors_list":vendors_list,
		"vendors_list2":vendors_list2,
		"vendors_list3":vendors_list3,
	}
	return render(request,"dashboard/sells.html",context)

@login_required
def Dashboard_sells_details(request,pk):
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	Boutique_ = Item.objects.filter(Boutique_name=objects).order_by('-timestamp')
	return render(request,"dashboard/details-sells.html",{"Boutique_":Boutique_})


def Dashboard_draft(request):
	BOUTIQUE_ = BOUTIQUE_REQUEST.objects.filter(user=request.user).filter(approved=True).order_by('-id')
	vendors_list = BOUTIQUE_[0:4]
	vendors_list2 = BOUTIQUE_[4:8]
	vendors_list3 = BOUTIQUE_[8:12]
	context = {
		"vendors_list":vendors_list,
		"vendors_list2":vendors_list2,
		"vendors_list3":vendors_list3,
	}
	return render(request,"dashboard/draft.html",context)


def Dashboard_draft_details(request,pk):
		# user = request.user.pk
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	Boutique_ = Item.objects.filter(Boutique_name=objects).order_by('-timestamp')
	return render(request,"dashboard/details-draft.html")


def Statics(request):
	return render(request, "dashboard/statics.html")


def payout(request):
	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'Bearer A101.OLQiCyqOpVwigKQQDu3CYlamZ1KTKQmhrbAZK85RIy4IiWh9d_up_lTadp_lfXdV.P3gvkY3PO28akjKYaDorm12QdfK',
	}

	data = { 
		"sender_batch_header": {
		"sender_batch_id": "Payouts_2020_100007",
		"email_subject": "You have a payout!",
		"email_message": "You have received a payout! Thanks for using our service!"
		}, 
		"items": [
			{
				"recipient_type": "EMAIL",
				"amount": { "value": "9.87", "currency": "USD" },
				"note": "Thanks for your patronage!",
				"sender_item_id": "201403140001",
				"receiver": "receiver@example.com",
				"recipient_wallet": "RECIPIENT_SELECTED",
				"notification_language": "en-US"
			} 
		] 
	}

	response = requests.post('https://api-m.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data)


# def news(request):
#     return render(request,"news.html")


# def news_details(request):
#     return render(request,"NewsDetail.html")
