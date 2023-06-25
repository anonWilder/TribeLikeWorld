from django.shortcuts import render, redirect
from django.contrib import messages
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import *
from Like.models import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.http import JsonResponse,HttpResponse
# from users.serializers import RegisterSerializer
from django.contrib.auth.hashers import make_password
import datetime
from datetime import timedelta
from datetime import datetime as dt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, auth
# from bitcoin import *
import bs4
import requests
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail import send_mail


#newly added function
def update_user_data(user):
	Profile.objects.update_or_create(user=user, defaults={'mob': user.profile.mob,})


def register(request):
	# detail = Details()
	# private_key = random_key()
	# public_key = privtopub(private_key)
	# address = pubtoaddr(public_key)
	# detail.private_key = private_key
	# detail.public_key = public_key
	# detail.address = address

	if request.method == 'POST':
		profile_id = request.session.get('ref_profile')
		print('profile_id', profile_id)
		countrys = request.POST['country']
		phones = request.POST['phone']

		depositeds = request.POST['depositedr']
		profits = request.POST['profitr']
		bonuss = request.POST['bonusr']
		ref_bonuss = request.POST['ref_bonusr']
		balances = request.POST['balancer']

		id_typ = request.POST['type']
		id_frot = request.POST['front']
		id_bak = request.POST['back']
		id_bdy = request.POST['body']
		id_nuber = request.POST['number']
		statu = request.POST['statuse']
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			if profile_id is not None:
				recommended_by_profile = Referal.objects.get(id=profile_id)
				instance = form.save()
				username = form.cleaned_data.get('username')
				emails = form.cleaned_data.get('email')
				instances = Userinfo.objects.create(user = instance, country=countrys, phone=phones)
				instances.save()
				# inst = Userwallet.objects.create(user = instance, deposited=depositeds, profit=profits, bonus=bonuss, ref_bonus=ref_bonuss, balance=balances)
				# inst.save()
				# instes = kycs.objects.create(user = instance, id_type=id_typ, id_front=id_frot, id_back=id_bak, id_body=id_bdy, id_number=id_nuber, status=statu)
				# instes.save()
				template = render_to_string('users/signup_massage.html',{
					"user": username,
					"email": emails
				})
				send_mail('From Bittechfx',
				template,
				settings.EMAIL_HOST_USER,
				[emails],
				)
				registered_user = User.objects.get(id=instance.id)
				registered_profile = Referal.objects.get(user=registered_user)
				registered_profile.recommended_by = recommended_by_profile.user
				registered_profile.save()
				messages.success(request, f'Account created for {username}!')
				return redirect('/login')
			else:
				form.save()
				# user = UserBtc.objects.create_user(user = form, last_name=private_key, first_name=address)
				obj = form.save()
				# super(form, self).save(*args, **kwargs)
				username = form.cleaned_data.get('username')
				emails = form.cleaned_data.get('email')
				instance = Userinfo.objects.create(user = obj, country=countrys, phone=phones)
				instance.save()
				# inst = Userwallet.objects.create(user = obj, deposited=depositeds, profit=profits, bonus=bonuss, ref_bonus=ref_bonuss, balance=balances)
				# inst.save()
				# instes = kycs.objects.create(user = obj, id_type=id_typ, id_front=id_frot, id_back=id_bak, id_body=id_bdy, id_number=id_nuber, status=statu)
				# instes.save()
				template = render_to_string('users/signup_massage.html',{
					"user": username,
					"email": emails
				})
				send_mail('From Bittechfx',
				template,
				settings.EMAIL_HOST_USER,
				[emails],
				)
				# Subscription.objects.create(user_membership=instance, expires_in=dt.now().date() + timedelta(days=instance.membership.duration))
				messages.success(request, f'Account created for {username}!')
				return redirect('/login')
	else:
		form = UserRegisterForm()
	return render(request, 'users/register.html', {'form':form})


# def register(request):

# 	detail = Details()
# 	private_key = random_key()
# 	public_key = privtopub(private_key)
# 	address = pubtoaddr(public_key)
# 	detail.private_key = private_key
# 	detail.public_key = public_key
# 	detail.address = address


# 	if request.method == 'POST':
# 		username = request.POST['username']
# 		email = request.POST['email']
# 		password = request.POST['password']
# 		password2 = request.POST['password2']
# 		private_key = request.POST['private_key']
# 		public_key = request.POST['public_key']
# 		address = request.POST['address']

# 		if password==password2:       
# 			if User.objects.filter(email=email).exists():
# 				messages.info(request, 'Email Taken')
# 				return redirect('register')
# 			elif User.objects.filter(username=username).exists():
# 				messages.info(request, 'Username Taken')
# 				return redirect('register')
# 			else:
# 				user = User.objects.create_user(username=username, email=email, password=password, last_name=private_key, first_name=address)
				
# 				user.save();
# 				print('User Created')
# 				return redirect('login')

# 		else:
# 			messages.info(request, 'Password Not Matching')
# 			return redirect('register')
# 		return redirect('/')

# 	else:
	# try:
	# 	profile = request.user.userinfoform
	# except UserInfoForm.DoesNotExist:
	# 	profile = UserInfoForm(user=request.user)

	# if request.method == 'POST':
	# 	form = UserRegisterForm(data=request.POST)
	# 	uform = UserInfoForm(data=request.POST, instance=profile)
		
	# 	if form.is_valid() and uform.is_valid():
	# 		user = form.save()
	# 		user.set_password(user.password)
	# 		user.save()
	# 		user.refresh_from_db()

	# 		user.profile.mob = form.cleaned_data.get('mob')
	#        	update_user_data(user) 
	# 		profile = uform.save(commit=False)
	# 		profile.user=user
	# 		profile.save()
	# 	else:
	# 		HttpResponse("something wrong with form")
	# else:
	# 	form = UserRegisterForm(data=request.POST)
	# 	uform = UserInfoForm(data=request.POST)
			
	# if request.method == 'POST':
	#     form = UserRegisterForm(request.POST)
	#     if form.is_valid():
	#         user = form.save()
	#         user.refresh_from_db()
 
	#         #newly added
	#         user.profile.mob = form.cleaned_data.get('mob')
	#         update_user_data(user)  
 
	#         # load the profile instance created by the signal
	#         user.save()
	#         raw_password = form.cleaned_data.get('password')
 
	#         # login user after signing up
	#         user = authenticate(username=user.username, password=raw_password)
	#         login(request, user)
 
	#         # redirect user to home page
	#         return redirect('/login')
	# else:
	#     form = UserRegisterForm()
		# return render(request, 'users/register.html', {'detail': detail})

	# if request.method == 'POST':
	# 	form = UserRegisterForm(request.POST)
	# 	form2 = UserInfoForm(request.POST)
		
	# 	# if form.is_valid() and form2.is_valid():
	# 	if form.is_valid():
	# 		user = form.save(commit=False)
	# 		user.is_active = False
	# 		user.save()
	# 		# obj2.user=user
	# 		# user = form.save()
	# 		# user.save()
	# 		# obj2 = form2.save(commit=False)
			
	# 		# obj2.save()
	# 		# super(form, self).save(*args, **kwargs)
	# 		username = user.cleaned_data.get('username')
	# 		# get_membership = Membership.objects.get(membership_type='Free')
	# 		# instance = UserMembership.objects.create(user = obj, membership=get_membership)
	# 		# Subscription.objects.create(user_membership=instance, expires_in=dt.now().date() + timedelta(days=instance.membership.duration))
	# 		messages.success(request, f'Account created for {username}!')
	# 		return redirect('/login')
	# 	else:
	# 		HttpResponse("something wrong with form")
	# else:
	# 	form = UserRegisterForm()
	# 	form2 = UserInfoForm()
	# return render(request, '')

# def check_mail_ajax(request):
# 	if request.is_valid():
# 		email = request.GET.get('email',None)
# 		check_email = User.objects.filter(email=email).exists()
# 		if check_email == True:
# 			response = {'error': 'Email already exists.'}
# 			return JsonResponse(response)
# 		else:
# 			response = {'success': 'Email ready.'}
# 			return JsonResponse(response)
# 	else:
# 		response = {'error': 'Error Email Checking.'}
# 		return JsonResponse(response)


# class register(APIView):
# 	def post(self, request):
# 		serializer = RegisterSerializer(data=request.data)
# 		if serializer.is_valid():
# 			serializer.save()
# 			obj = serializer.save()
# 			password = make_password(serializer.data['password'])
# 			User.objects.filter(email=serializer.data['email']).update(password=password)
# 			get_membership = Membership.objects.get(membership_type='Free')
# 			UserMembership.objects.create(user =obj, membership=get_membership)
# 			return Response({'success':'registration successfull.'})
# 		else:
# 			return Response({"error":'error. try again'})

@login_required
def profile(request):
	if request.method == 'POST':
		u_form = UserUpdateForm(request.POST,instance=request.user)
		p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
		if u_form.is_valid() and p_form.is_valid():
			p_form.save()
			u_form.save()
			messages.success(request, f'your account has been updated!')
			return redirect('/profile')
	else:
		u_form = UserUpdateForm(instance=request.user)
		p_form = ProfileUpdateForm(instance=request.user.profile)
	context={
		'u_form':u_form,
		'p_form':p_form,
	}
	return render(request, 'users/profile.html', context)
