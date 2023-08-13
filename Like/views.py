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
from django.http import HttpResponseRedirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, ContactForm, ContactMessage
from .models import *
from django.http import HttpResponse,JsonResponse
from users.models import *
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMessage,EmailMultiAlternatives,send_mail
from paypal.standard.forms import PayPalPaymentsForm
import uuid
import random
import string
import requests
from django.core import serializers
import json
import stripe
from django.core.exceptions import MultipleObjectsReturned
import subprocess
import time
# import Paystack
from django.shortcuts import render
from .models import Main_Category, Order, counter
# paystack.api_key = settings.PAYSTACK_SECRET_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
	if request.user.is_authenticated:
		order = Order.objects.get(user=request.user, ordered=False)
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
	category = Main_Category.objects.all().order_by('-id')
	boutique = BOUTIQUE_REQUEST.objects.all().order_by('-id')
	queryset = Item.objects.all()
	query = request.GET.get('q')
	if query:
		queryset = queryset.filter(
			Q(title__icontains=query) |
			Q(description__icontains=query)
		).distinct()
	context = {
		'queryset':queryset,
		'boutique':boutique,
		'category':category
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
	category = Main_Category.objects.all().order_by('-id')
	if request.user.is_authenticated:
		order = Order.objects.get(user=request.user, ordered=False)
	else:
		order = False
	amount = order.get_total()
	
	# 	tax_fee = 3.49
	# amount = int(order.get_total() + tax_fee)
	
	context = {
		'order': order,
		'DISPLAY_COUPON_FORM': False,
		'amount':amount,
		'category':category,
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
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	order = 0
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
		# if request.user.is_authenticated:
		# 	order = Order.objects.get(user=self.request.user, ordered=False)
		# else:
		order = 0
		featured_post = Item.objects.filter(futured=True,draft=True).order_by('-timestamp')[:10]
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
	Boutique_ = item.Boutique_name
	order_item, created = OrderItem.objects.get_or_create(
		item=item,
		user=request.user,
		Boutique_nam = Boutique_,
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

def main_category(request, id):
	category = Main_Category.objects.all().order_by('-id')
	boutique = BOUTIQUE_REQUEST.objects.all().order_by('-id')
	if id:
		main_category = get_object_or_404(Main_Category, id=id)
		post = Category.objects.filter(Main_Category=main_category)
	template = "main_category.html"
	context = {
		'post': post,
		'category': category,
		'boutique':boutique,
	}
	return render(request, template, context)

def list_category(request, id):
	category = Main_Category.objects.all().order_by('-id')
	boutique = BOUTIQUE_REQUEST.objects.all().order_by('-id')
	if id:
		sub_category = get_object_or_404(Sub_Category, id=id)
		post = Item.objects.filter(sub_category=sub_category)
	template = "category_details.html"
	context = {
		'post': post,
		'category': category,
		'boutique':boutique,
	}
	return render(request, template, context)

def list_category_item(request, id):
	category = Main_Category.objects.all().order_by('-id')
	boutique = BOUTIQUE_REQUEST.objects.all().order_by('-id')
	if id:
		categorys = get_object_or_404(Category, id=id)
		post = Item.objects.filter(category=categorys)
	template = "category_details.html"
	context = {
		'post': post,
		'category': category,
		'boutique':boutique,
	}
	return render(request, template, context)




def about_us(request):
	category = Main_Category.objects.all().order_by('-id')
	const = {
		"category":category,
	}
	return render(request,'about-us.html',const)

def contact(request):
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=self.request.user, ordered=False)
	# else:
	order = 0
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
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	order = 0
	category = Main_Category.objects.all().order_by('-id')
	shops = Item.objects.all().order_by('-timestamp')
	vendors_list = BOUTIQUE_REQUEST.objects.filter(approved=True).order_by('-id')
	const = {
		'order':order,
		"shops":shops,
		"category":category,
		"vendors_list":vendors_list,
	}
	return render(request,"shop.html",const)

def sell_here(request):
	category = Main_Category.objects.all().order_by('-id')
	const = {
		"category":category,
	}
	return render(request,"sell_here.html",const)

@login_required
def ListItem(request):
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	order = 0
	vendors_list = BOUTIQUE_REQUEST.objects.filter(user=request.user).order_by('-id')
	category_list = Category.objects.all().order_by('-id')
	category = Main_Category.objects.all().order_by('-id')
	subcategory_list = Sub_Category.objects.all().order_by('-id')
	try:
		if request.method == "POST":
			pod = Item()
			pod.user=request.user
			pod.title = request.POST.get("title")
			pod.price = request.POST.get("price")
			pod.discount_price = request.POST.get("discount_price")
			pod.shiping_fee =  request.POST.get("shiping_fee")
			boutique_name =  request.POST.get("Boutique_name")
			pod.Boutique_name = BOUTIQUE_REQUEST.objects.get(Boutique_name=boutique_name)
			category = request.POST.get("category")
			pod.category = Category.objects.get(name=category)
			sub_categorys = request.POST.get("sub_category")
			try:
				pod.sub_category = Sub_Category.objects.get(name=sub_categorys)
			except Sub_Category.MultipleObjectsReturned:
				pod.sub_category = Sub_Category.objects.filter(name=sub_categorys).first()
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
				
			send_mail('From Tribe Like',
			template,
			settings.EMAIL_HOST_USER,
			['francisdaniel140@gmail.com','likegroupinc@gmail.com'],
			)
			messages.success(request, f'Item Successfully added !')
	except Exception as e:
		# send an email to ourselves
		messages.warning(request, str(e))
	return render(request, "dashboard/list-item.html",{"vendors_list":vendors_list,'order':order,'category':category,"category_list":category_list,"subcategory_list":subcategory_list})

@login_required
def all_soled_iteam(request):
	pks = request.session['pk']
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pks)
	# print("this ggggg",Boutique_)
	Boutique_ =  OrderItem.objects.filter(Boutique_nam=objects, ordered=True)
	print("hhhhhh",Boutique_)


	# objects = Order.objects.filter(user_id=request.user.id)
	# id_ = request.user.id
	# ordered_list = PayoutUserList.objects.all()
	# objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	# Boutique_ = Item.objects.filter(Boutique_name=objects, ).order_by('-timestamp')
	

	# ordered_list = OrderItem.objects.filter(user=objects).order_by('-timestamp')
	# objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	# Boutique_ = Item.objects.filter(Boutique_name=objects).order_by('-timestamp')
	# ordered_list = OrderItem.objects.filter(item=Boutique_, ordered=True).order_by('-timestamp')
	return render(request,"dashboard/all-soled.html",{"Boutique_":Boutique_})


@login_required
def sell_form(request):
	category = Main_Category.objects.all().order_by('-id')
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	try:
		order = 0
		if request.method == "POST":
			user_email =  request.user.email
			pod = BOUTIQUE_REQUEST()
			pod.user=request.user
			pod.Boutique_name = request.POST.get("Boutique_name")
			pod.items_to_sell = request.POST.get("items_to_sell")
			pod.number =  request.POST.get("number")
			pod.where_else_you_sell = request.POST.get("where_else_you_sell")
			pod.social_media =  request.POST.get("social_media")
			pod.country =  request.POST.get("country")
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
			
			# subject = 'From Tribe Like'
			# from_email = settings.EMAIL_HOST_USER
			# recipient_list = [user_email,'tribelikeventures@gmail.com']
			# template = render_to_string('emails/BOUTIQUE_REQUEST_EMAIL_TEM.html',{"title":"text file","email": user_email})
			# cont = strip_tags(template)
			# email = EmailMultiAlternatives(subject,cont, from_email, recipient_list)
			# email.attach_alternative(template, "text/html")
				
			# image_path = 'http://127.0.0.1:8000/static/images/t.png'
			# with open(image_path, 'rb') as f:
			# 	image_data = f.read()
			# 	email.attach("http://127.0.0.1:8000/static/images/tribe_like_fun_2.png", image_data, "image/jpg")

			# # Set the Content-ID header for the embedded image
			# email.mixed_subtype = 'related'
			# email.attach_related(image_data, 'image/jpg', 'unique_cid')
			# email.send()
			template = render_to_string('emails/BOUTIQUE_REQUEST_EMAIL_TEM.html',{"title":"text file","email": user_email})
			send_mail('From Tribe Like',
			template,
			settings.EMAIL_HOST_USER,
			[user_email,'tribelikeventures@gmail.com'],
			)
			messages.success(request, f'Request has been sent Successfully !')
			return redirect('/successfully')
		else:
			return render(request,"sell_form.html",{'order':order,'category':category})
	except Exception as e:
		# send an email to ourselves
		messages.warning(request, str(e))

def successfully(request):
	return render(request,"successful.html")

def how_to_sell(request):
	category = Main_Category.objects.all().order_by('-id')
	const = {
		"category":category,
	}
	return render(request,'how-to-sell.html',const)

def vendors(request):
	# if request.user.is_authenticated:
	# 	if Order.objects.get(user=request.user, ordered=False) == None:
	# 		order
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	order = 0
	category = Main_Category.objects.all().order_by('-id')
	vendors_list = BOUTIQUE_REQUEST.objects.filter(approved=True).order_by('-id')
	vendors_count = BOUTIQUE_REQUEST.objects.filter(approved=True)
	# for i in vendors_count:
	#     n = i.user
	#     print(n.count())
	# single_count = vendors_count.filter(user=request.user).count()
	return render(request,"vendors.html",{'order':order,'vendors_list':vendors_list,'category':category})

def country_filter(request):
	order = 0
	category = Main_Category.objects.all().order_by('-id')
	countrys = request.GET.get('country')
	if countrys:
		vendors_list = BOUTIQUE_REQUEST.objects.filter(approved=True, country=countrys).order_by('-id')
		vendors_count = BOUTIQUE_REQUEST.objects.filter(approved=True)
	return render(request,"vendorsfilter.html",{'order':order,'vendors_list':vendors_list,'category':category,"countrys":countrys})

def VendorDetailView(request, pk):
	# if request.user.is_authenticated:
	# 	order = Order.objects.get(user=request.user, ordered=False)
	# else:
	order = 0
	category = Main_Category.objects.all().order_by('-id')
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pk)
	# print(objects)
	latest = Item.objects.filter(Boutique_name=objects).order_by('-timestamp')
	# print("this it",latest)


	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/successfully/') 


	# object = Item.objects.filter(item=post)order.items.filter(item__id=item.id).exists():
	featured_post = Item.objects.filter(futured=True).order_by('-timestamp')[:3]
	context = {
		'object': objects,
		'category':category,
		'latest': latest,
		'order':order,
		'futureds': featured_post,
		'form': ContactForm()
	}
	return render(request, 'vendor_details.html', context)


def contact(request):
	category = Main_Category.objects.all().order_by('-id')
	
	if request.method == 'POST':
		form = ContactMessage(request.POST)
		if form.is_valid():
			form.save()
			return redirect('/successfully/')

	const = {
		"category":category,
	}
	context = {
		'form': ContactMessage()
	}
	return render(request,"contact.html",const)

# def about_us(request):
# 	category = Main_Category.objects.all().order_by('-id')
# 	if request.user.is_authenticated:
# 		order = Order.objects.get(user=self.request.user, ordered=False)
# 	else:
# 		order = False
# 	counters = counter.objects.all()
# 	return render(request,"about-us.html",{'order':order,'counter':counters, "category":category})



def about_us(request):
    category = Main_Category.objects.all().order_by('-id')
    
    if request.user.is_authenticated:
        order = Order.objects.get(user=request.user, ordered=False)
    else:
        order = False
    
    counters = counter.objects.all()
    
    return render(request, "about-us.html", {'order': order, 'counter': counters, 'category': category})



def terms(request):
	return render(request,"terms.html")


@login_required
def Dashboard(request,pk):
	request.session['pk'] = pk
	pks = request.session['pk']
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pks)
	# print("this ggggg",Boutique_)
	soled =  OrderItem.objects.filter(Boutique_nam=objects, ordered=True)
	print("hhhhhh",soled)
	BOUTIQUE_ = BOUTIQUE_REQUEST.objects.filter(user=request.user).filter(approved=True).order_by('-id')
	vendors_list = BOUTIQUE_[0:4]
	vendors_list2 = BOUTIQUE_[4:8]
	vendors_list3 = BOUTIQUE_[8:12]
	context = {
		"vendors_list":vendors_list,
		"vendors_list2":vendors_list2,
		"vendors_list3":vendors_list3,
	}
	return render(request,"dashboard/dashboad.html",context)


@login_required
def Dashboard_sells(request):
	BOUTIQUE_ = BOUTIQUE_REQUEST.objects.filter(user=request.user).filter(approved=True).order_by('-id')
	context = {
		"vendors_list":BOUTIQUE_,
	}
	return render(request,"dashboard/sells.html",context)

@login_required
def Dashboard_sells_details(request):
	pk = request.session['pk']
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



def Dashboard_buys(request,pk):
		# user = request.user.pk
	objects = get_object_or_404(Order, pk=pk)
	# print(objects)
	# oders = Order.objects.filter(user_id=request.user.id, ordered=True).order_by('-start_date')
	model2_data = objects.OrderItem.all()
	for i in model2_data:
		print(i)
	return render(request,"dashboard/buys.html",{'buys':oders})

@login_required
def Statics(request):
	pks = request.session['pk']
	objects = get_object_or_404(BOUTIQUE_REQUEST, pk=pks)
	# print("this ggggg",Boutique_)
	total_orderd =  OrderItem.objects.filter(Boutique_nam=objects, ordered=True)
	bt = []
	for i in total_orderd:
		list_ = i.Boutique_nam
	print(bt)
	total_unorderd =  OrderItem.objects.filter(Boutique_nam=objects, ordered=False)
	# delivered =  Order.objects.filter(Boutique_nam=objects, being_delivered=False)
	data ={
		"total_orderd":total_orderd.count(),
		"total_unorderd":total_unorderd.count(),
		"total_orderd_chart":total_orderd,
		"total_unorderd_chart":total_unorderd
	}
	print("hhhhhh",data['total_orderd_chart'])
	return render(request, "dashboard/statics.html",data)

@login_required
def Content(request):
	return render(request, "dashboard/content.html")

@login_required
def payout(request):
	ordered_list = PayoutUserList.objects.all()
	data = serializers.serialize("json", ordered_list)
	data = json.loads(data)
	# return JsonResponse(data,safe=False)
	list_ = data[0]['fields']
	extra = {"amount": {"value": 9.87, "currency": "USD"}}
	dest = list_.copy()
	list_.update(extra)
	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'Bearer A21AAIPhFcyl-7RCv9QeM_8pTqZvGlJBjc1bMauRoiWd8AD8CFlC9w3bOYr4K3oI4ON6OyTA7y1mBdGcyxI49LMTBZ9U0l5ew',
	}
	data = { 
		"sender_batch_header": {
			"sender_batch_id": "Payouts_2020_100009",
			"email_subject": "You have a payout!",
			"email_message": "You have received a payout! Thanks for using our service!"
		}, 
		"items": [
			{
				"recipient_type": "EMAIL",
				"amount": {
					"value": "10.00",
					"currency": "USD"
				},
				"note": "Thanks for your patronage!",
				"sender_item_id": "2014031400801",
				"receiver": "kwebify1@gmail.com",
				"notification_language": "en-US"
			}
		]
	}
	response = requests.post('https://api.sandbox.paypal.com/v1/payments/payouts', headers=headers, data=data)
	# if response.status_code == 200:
	print("ll",response.text)
	print("ld",response)
	result = response.json()
	print("lg",result)
		# return JsonResponse(result,safe=False)





def paypal_payout(request):
	# PayPal API endpoint
	endpoint = 'https://api.paypal.com/v1/payments/payouts'

	# PayPal access token
	access_token = '<YOUR_PAYPAL_ACCESS_TOKEN>'

	# Prepare the request headers
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {access_token}'
	}

	# Prepare the payout data
	payout_data = {
		"sender_batch_header": {
			"sender_batch_id": "<UNIQUE_SENDER_BATCH_ID>",
			"email_subject": "Payment from XYZ Store"
		},
		"items": [
			{
				"recipient_type": "EMAIL",
				"amount": {
					"value": "10.00",
					"currency": "USD"
				},
				"note": "Thank you for your service!",
				"receiver": "<VENDOR_1_EMAIL>"
			},
			{
				"recipient_type": "EMAIL",
				"amount": {
					"value": "15.00",
					"currency": "USD"
				},
				"note": "Payment for recent purchase",
				"receiver": "<VENDOR_2_EMAIL>"
			},
			# Add more vendor payouts as needed
		]
	}

	# Convert the payout data to JSON
	payload = json.dumps(payout_data)

	# Send the POST request to PayPal Payouts API
	response = requests.post(endpoint, headers=headers, data=payload)

	# Handle the response
	if response.status_code == 201:
		# Payout successful
		response_data = response.json()
		payout_batch_id = response_data['batch_header']['payout_batch_id']
		return HttpResponse(f"Payout successful! Batch ID: {payout_batch_id}")
	else:
		# Payout failed
		error_message = response.json()['message']
		return HttpResponse(f"Payout failed! Error: {error_message}")


# def news(request):
#     return render(request,"news.html")


# def news_details(request):
#     return render(request,"NewsDetail.html")

def single_page(request):
	return render(request, "post-single.html")

def editorial_page(request):
	blog_posts = BlogPost.objects.all()
	return render(request, 'news.html', {'blog_posts': blog_posts})

def single_post(request, slug):
	post = get_object_or_404(BlogPost, slug=slug)
	return render(request, 'post-single.html', {'post': post})


def terms_view(request):
	return render(request, 'terms.html')
	


import requests
import subprocess
import time


ODOO_SERVER_URL = "http://164.92.155.135:2000/Login/"  # Replace with your Odoo server URL
ODOO_SERVER_COMMAND = "sudo systemctl restart apache2"

def is_server_up(url):
	try:
		response = requests.get(url)
		return response.status_code == 502
	except requests.ConnectionError:
		return False

def restart_odoo_server(command):
	os.system("sudo service apache2 restart")  # Adjust this command based on your OS and Apache setup
	# subprocess.run(["systemctl", "restart", "apache2"])
	# subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
	while True:
		if not is_server_up(ODOO_SERVER_URL):
			print("Odoo server is down. Restarting...")
			restart_odoo_server(ODOO_SERVER_COMMAND)
		time.sleep(60)  # Adjust the interval as needed (e.g., every 60 seconds)

if __name__ == "__main__":
	main()


def User_dashboad(request):
	soled = Order.objects.filter(user=request.user, ordered=True)
	# main()
	for i in soled:

		print(i.items)
	return render(request, 'user-dashboard/bought-iteam.html',{"buys":soled})
