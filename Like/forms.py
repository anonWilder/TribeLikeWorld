from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from tinymce.widgets import TinyMCE
from .models import ContactFormEntry
from .models import ContactMessageEntry


PAYMENT_CHOICES = (
    # ('p', 'Paystack'),
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100 form-control form-control-md',
        }))
    shipping_zip = forms.CharField(required=False)

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100 form-control form-control-md',
        }))
    billing_zip = forms.CharField(required=False)

    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-md mr-1 mb-2',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    paystackToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactFormEntry
        fields = ['name', 'email', 'message']


class ContactMessage(forms.ModelForm):
    class Meta:
        model = ContactMessageEntry
        fields = ['name', 'email', 'message']