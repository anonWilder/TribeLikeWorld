from django.urls import path
from . import views
from .views import (
    # ItemDetailView,
    CheckoutView,
    HomeView,
    IndexView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    search,
    welcome_user,
    RequestRefundView
)

app_name = 'core'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('menu/', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<int:pk>', views.ItemDetailView, name='product'),
    path('add-to-cart/<int:pk>', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<int:pk>', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<int:pk>', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('search/', search, name='search'),
    path('welcome_user/', welcome_user, name='welcome_user'),

    # path('categories/', views.Categories.as_view(), name='categories'),
    # path('category/<int:pk>', views.CategoryView.as_view(), name='category'),
    path('category/<int:pk>', views.list_category, name='list_category'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('sell-here/', views.sell_here, name='sell_here'),
    path('sell-form/', views.sell_form, name='sell_form'),
    path('all-vendors/', views.vendors, name='vendors'),
    path('successfully/', views.successfully, name='successfully'),

    path('contact-us/', views.contact, name="contact"),
    # path('news-page/', views.news, name="news"),
    # path('news-details/', views.news_details, name="news_details"),
    path('vendor-Details/<int:pk>', views.VendorDetailView, name='vendors'),
    path('shop/', views.shop, name="shop"),
    path('dashboard_sells/', views.Dashboard_sells, name="Dashboard_sells"),
    path('draft_sells/', views.Dashboard_draft, name="Dashboard_draft"),
    path('payment-completed/', views.payment_completed_view, name="payment-completed"),
    path('payment-failed/', views.payment_failed_view, name="payment-failed"),
    path('statics/', views.Statics, name="statics"),
    path('list-item/', views.ListItem, name="ListItem"),
    path('paypal_payments/<payment_option>/', views.PaypalPayment, name="paypal_payment"),
    path('paypal_invoice', views.InvoicePayment, name="paypal_invoice"),
    path('sells-details/<int:pk>', views.Dashboard_sells_details, name='sells_details'),

    path('how-to-sell/', views.how_to_sell, name='how_to_sell'),
]
