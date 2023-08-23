from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('register/', CustomerCreateView.as_view(), name='register_customer'),
    path('login/', CustomerLogin.as_view(), name='login'),

    path('website/', WebisteView.as_view(), name='website'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('customer-list/', CreateCustomerView.as_view(), name='customer_list'),
    path('Customer/list/ajax', ListCustomerViewJson.as_view(), name='Customer-list-ajax'),
    path('Customer/delete/<int:pk>', DeleteCustomerView.as_view(), name='Customer-user-delete'),
    path('Customer/update/<int:pk>', CustomerUpdateView.as_view(), name='Customer-user-update'),
    path('change_customer_status/<int:pk>/<str:is_active>/',change_customer_status, name='change_customer_status'),

    path('export-excel/', CustomerExportView.as_view(), name='create_export_customer'),


    path('customer-address-list/', ListAddressView.as_view(), name='customer_address_list'),

    # path('addresses/', ListCustomerAddressView.as_view(), name='address_form'),

    # path('addresses/', CustomerAddressCreate.as_view(), name='address_form'),
    # path('addresses/', views.customer_address_create, name='address_form'),
    path('addresses/', CustomerAddressCreateView.as_view(), name='address_form'),
    path('address/list/ajax', ListAddressViewJson.as_view(), name='address_list_ajax'),

    path('addresses/<int:pk>', AddressUpdateView.as_view(), name='addedit'),
    path('addresses/del/<int:pk>', AddressDeleteView.as_view(), name='add_delete'),


    path('address/edit/<int:pk>', UpdateAddressView.as_view(), name='address_edit'),
    path('address/delete/<int:pk>', DeleteAddressView.as_view(), name='address_delete'),

    path('contacts/', CreateContactView.as_view(), name='contact'),
    path('customer-contactus-list/', ListContactView.as_view(), name='contactus_list'),
    path('contactus/list/ajax', ListContactViewJson.as_view(), name='contactus_list_ajax'),

]