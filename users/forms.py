from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from users.models import Profile


class UserRegisterForm(UserCreationForm):
	email = forms.EmailField(widget=forms.EmailInput(attrs={
		'class': 'form-control ps-15 bg-transparent',
		'placeholder': 'Email.......',

	}))
	# mob = forms.IntegerField() # newly added

	class Meta:
		model = User
		fields = ('first_name','last_name','username', 'email')
		widgets = {
			'first_name':forms.TextInput(attrs={'class':'','placeholder':'First Name'}),
			'last_name':forms.TextInput(attrs={'class':'','placeholder':'Last Name'}),
			'username':forms.TextInput(attrs={'class':'','placeholder':'username'}),
			'email':forms.TextInput(attrs={'class':'','placeholder':'Email'}),
			
		}

	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['email'].label = ""
	# 	self.fields['username'].label = ""

# class UserInfoForm(forms.ModelForm):
# 	mobile = forms.IntegerField(widget=forms.TextInput(attrs={
# 		'class': 'form-control ps-15 bg-transparent',
# 		'placeholder': 'Phone Number',

# 	}))
# 	class Meta():
# 		model = Profile
# 		fields = ['mobile']


class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['image']