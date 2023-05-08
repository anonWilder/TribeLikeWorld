from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django import forms
# from Template.models import User

# class ProfileInfo(models.Model):
# 	user = models.OneToOneField(User, on_delete=models.CASCADE)
# 	mobile = models.IntegerField(blank=True,null=True)
# 	def __str__(self):
# 		return f'{self.user.username} info'


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(default='default.png', upload_to='profiles')
	
	

	def __str__(self):
		return f'{self.user.username} Profile'

	def save(self, *args, **kwargs):
		super().save()
		img = Image.open(self.image.path)
		if img.height > 300 or img.width > 300:
			output_size = (300, 300)
			img.thumbnail(output_size)
			img.save(self.image.path)
