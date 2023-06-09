from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from users.models import Profile as profile
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from .utils import generate_ref_code


# CATEGORY_CHOICES = (
#     ('S', 'Shirt'),
#     ('SW', 'Sport wear'),
#     ('OW', 'Outwear')
# # )

# class Category(models.Model):
#     name = models.CharField(max_length=100, verbose_name='分类名称')

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "cate"
#         verbose_name_plural = verbose_name

#     def get_absolute_url(self):
#         return reverse('core:category', kwargs={'pk': self.pk})

class Main_Category(models.Model):
    name = models.CharField(max_length=100,default=False)
    icons =  models.ImageField(blank=True,null=True)

    def __str__(self):
        return self.name
   
class Category(models.Model):
    Main_Category = models.ForeignKey(Main_Category,on_delete=models.CASCADE,default=False)
    name = models.CharField(max_length=100,default=False)
    icons =  models.ImageField(blank=True,null=True)

    def __str__(self):
        return self.name

class Sub_Category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=False)
    name = models.CharField(max_length=100,default=False)
    # slug = models.SlugField(max_length=250, unique=True)

    # class Meta:
    #     ordering = ('name',)
    #     verbose_name = "category"
    #     verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('core:category', args=[self.id])

    def __str__(self):
        return self.name


LABEL_CHOICES = (
    ('BEST SELLER', 'BEST SELLER'),
    ('MOST POPULAR', 'MOST POPULAR'),
    ('NEW ARRIVALS', 'NEW ARRIVALS')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    preview_price = models.CharField(max_length=100,default="0.00")
    price = models.FloatField()
    user = models.ForeignKey(to=profile, on_delete=models.CASCADE)
    # item_type = models.CharField(max_length=50, choices=(
    #     ('1', 'p'), ('0', 't')), default='1')
    discount_price = models.FloatField(blank=True, null=True)
    seasson = models.CharField(choices=LABEL_CHOICES, max_length=150, default='NEW ARRIVALS')
    # slug = models.SlugField(max_length=250, unique=True)
    Boutique_name = models.ForeignKey('BOUTIQUE_REQUEST', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Sub_Category, on_delete=models.CASCADE,default=False)
    overview = models.TextField(default='False')
    description = models.TextField(default='False')
    approved = models.BooleanField(default=False)
    futured = models.BooleanField(default=False)
    image = models.ImageField(blank=True,null=True,default="/static/images/banner3.png")
    image2 = models.ImageField(blank=True,null=True,default="/static/images/banner3.png")
    # breakfast = models.BooleanField(default=False)
    timestamp = models.DateTimeField(blank=True, null=True)
    created_on = models.DateField(auto_now=True)
    item_created_date = models.DateField(auto_now=True)
    # image_path = models.CharField(max_length=200)
    # category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)

    def __str__(self): 
        return f'{self.title} - {self.pk}'

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'pk': self.pk
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'pk': self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'pk': self.pk
        })

class BOUTIQUE_REQUEST(models.Model):
    user =  models.ForeignKey(User,on_delete=models.CASCADE,default=False)
    Boutique_name = models.CharField(max_length=140)
    items_to_sell = models.CharField(max_length=200)
    number =  models.CharField(max_length=140)
    where_else_you_sell = models.CharField(max_length=900)
    social_media =  models.TextField()
    approved = models.BooleanField(default=False)
    about_your_business = models.TextField()
    brand_logo = models.ImageField(blank=True,null=True)
    brand_banner = models.ImageField(blank=True,null=True)
    hear_about_us = models.CharField(max_length=900)
    products_image1 = models.ImageField(blank=True,null=True)
    products_image2 = models.ImageField(blank=True,null=True)
    products_image3 = models.ImageField(blank=True,null=True)
    products_image4 = models.ImageField(blank=True,null=True)

    def __str__(self):
        return f'{self.Boutique_name}'

    def get_absolute_url(self):
        return reverse("core:vendors", kwargs={
            'pk': self.pk
        })
    
    def get_absolute_urls(self):
        return reverse("core:sells_details", kwargs={
            'pk': self.pk
        })



class PostImage(models.Model):
    post = models.ForeignKey(Item, default=None, on_delete=models.CASCADE)
    image = models.FileField(upload_to = 'images/')

    def __str__(self):
        return self.post.title

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50,blank=True, null=True)
    paypal_order_id = models.CharField(max_length=100,blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class contactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    massage = models.TextField()

    def __str__(self):
        return self.email
    
class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)



class Referal(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	code = models.CharField(max_length=12, blank=True)
	recommended_by= models.ForeignKey(User,on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user.username}-{self.code}"

	def get_recommended_referals(self):
		qs = Referal.objects.all()
		# my_recs = [p for p in qs if p.recommended_by == self.user]
		my_recs = []
		for profile in qs:
			if profile.recommended_by == self.user:
				my_recs.append(profile)
		return my_recs

	def save(self, *args, **kwargs):
		if self.code == "":
			code = generate_ref_code()
			self.code = code
		super().save(*args, **kwargs)



class counter(models.Model):
    name = models.CharField(max_length=30)
    count = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Top_Brands(models.Model):
    brands_logo = models.ImageField(blank=True, null=True, default=False)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id