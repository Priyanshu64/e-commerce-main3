from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, TemplateView, ListView, CreateView
from django.views import View
from django.shortcuts import render, redirect,reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .forms import CreateCustomerUserForm, CreateCustomerForm, EditCustomerUserForm, CustomerAddressForm, CustomerContactForm
from application.custom_classes import AjayDatatableView, AdminRequiredMixin, UserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Customer, CustomerAddress, CustomerContact
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .models import CustomerAddress
from django.shortcuts import get_object_or_404
import xlsxwriter
User = get_user_model()
from django.contrib.auth.decorators import login_required




class CustomerCreateView(CreateView):
    model = Customer
    form_class = CreateCustomerForm
    user_form_class = CreateCustomerUserForm
    template_name = 'customer/register.html'
    success_message = "Customer created successfully"
    success_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        user_form = self.user_form_class()
        return render(request, self.template_name, {'form': form, 'user_form': user_form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user_form = self.user_form_class(request.POST)
        
        if all([form.is_valid(), user_form.is_valid()]):
            user = user_form.save(commit=False)
            user.type = 'customer'
            user.save()

            email = user_form.cleaned_data['email']
            if Customer.objects.filter(user__email=email).exists():
                return render(request, self.template_name, {'form': form, 'user_form': user_form})

            phone_number = form.cleaned_data['phone_number']
            if Customer.objects.filter(phone_number=phone_number).exists():
                return render(request, self.template_name, {'form': form, 'user_form': user_form})

            customers = form.save(commit=False)
            customers.user = user
            customers.save()

            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            if 'phone_number' in form.errors:
                messages.error(request, "This phone number is already in use.")
            if 'email' in user_form.errors:
                messages.error(request, "This email is already in use.")
            return render(request, self.template_name, {'form': form, 'user_form': user_form})
    


class CustomerLogin(View):
    success_message = 'You have successfully logged in.'
    failure_message = 'Please check credentials.'

    def get(self, request, *args, **kwargs):
        return render(request, 'customer/login.html')

    def post(self, request):
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username,
                            password=password)
        if user is not None:
            login(request, user)
            messages.success(request, self.success_message)
            return HttpResponseRedirect(reverse('website'))
        else:
            messages.error(request, self.failure_message)
            return HttpResponseRedirect(reverse('login'))


class WebisteView(TemplateView):
    template_name = 'customer/index.html'

class ContactView(TemplateView):
    template_name = 'customer/contact.html'


    
class CreateCustomerView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'customer/list.html'
    
    
class ListCustomerViewJson(AdminRequiredMixin, AjayDatatableView):
    model = Customer
    columns = ['first_name', 'phone_number', 'user.email','user.is_active', 'actions']
    exclude_from_search_columns = ['actions']
    extra_search_columns = ['first_name','phone_number']

    def get_initial_queryset(self):
        return self.model.objects.all()

    def render_column(self, row, column):
        if column == 'user.is_active':
            if row.user.is_active:
                is_active = False
                _kwargs = {'pk': row.user.id, 'is_active': is_active}
                return '<a href={} ><span class="badge badge-success">Active</span></a>'.format(
                    reverse('change_customer_status', kwargs=_kwargs))
            else:
                is_active = True
                _kwargs = {'pk': row.user.id, 'is_active': is_active}
                return '<a href={} ><span class="badge badge-danger">Inactive</span></a>'.format(
                    reverse('change_customer_status', kwargs=_kwargs))

        if column == 'actions':
            edit_action = '<a href={} role="button" class="btn btn-warning btn-xs mr-1 text-white">Edit</a>'.format(
                reverse('Customer-user-update', kwargs={'pk': row.pk}))
            delete_action = '<a href="javascript:;" class="remove_record btn btn-danger btn-xs" data-url={} role="button">Delete</a>'.format(
                reverse('Customer-user-delete', kwargs={'pk': row.pk}))
            # return edit_action + delete_action
        else:
            return super(ListCustomerViewJson, self).render_column(row, column)


class DeleteCustomerView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Customer
    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)


def change_customer_status(request, pk, is_active):
    user = Customer.objects.filter(user__id=pk).first().user
    user.is_active = is_active
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class CustomerUpdateView(AdminRequiredMixin, LoginRequiredMixin,UpdateView):
    model = Customer
    form_class = CreateCustomerForm
    user_form_class = EditCustomerUserForm
    template_name = 'customer/form.html'
    success_message = "Customer updated successfully"
    success_url = reverse_lazy('customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(instance=self.object)
        if 'user_form' not in context:
            context['user_form'] = self.user_form_class(instance=self.object.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        user_form = self.user_form_class(request.POST, instance=self.object.user)
        if all([form.is_valid(), user_form.is_valid()]):
            user = user_form.save(commit=False)
            user.type = 'customer'
            user.save()
            customers = form.save(commit=False)
            customers.user = user
            customers.save()
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            messages.error(request, "Error: This email is already exists")
            return render(request, self.template_name, {'form': form, 'user_form': user_form})


class CustomerExportView(View):
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()

        output = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        output['Content-Disposition'] = 'attachment; filename=customer_export.xlsx'
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        header = ['First Name', 'Phone Number']
        for col_num, header_label in enumerate(header):
            worksheet.write(0, col_num, header_label)

        for row_num, customer in enumerate(customers, start=1):
            row_data = [customer.first_name, customer.phone_number]
            for col_num, value in enumerate(row_data):
                worksheet.write(row_num, col_num, value)

        workbook.close()
        return output


# class ListAddressView(TemplateView):
#     template_name = 'customer/address_list.html'
#
#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         addresses = CustomerAddress.objects.all()
#
#         context['addresses'] = addresses
#         return context
class ListAddressView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'customer/address_list.html'


class CustomerAddressCreateView(LoginRequiredMixin, CreateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = 'customer/address_form.html'
    success_url = reverse_lazy('address_form')

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse_lazy('login'))
        print(request.user)
        queryset = CustomerAddress.objects.filter(customer_id=request.user)
        context = {'data': queryset}
        form = self.form_class()
        return render(request, self.template_name, {'form': form, **context})

    def post(self, request,* args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.customer = self.request.user
            address.save()
            messages.success(request, ' Submit Successfully.')
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})

# @login_required
# def customer_address_create(request):
#     if request.method == 'POST':
#         form = CustomerAddressForm(request.POST)
#         if form.is_valid():
#             address = form.save(commit=False)
#             address.customer = request.user
#             address.save()
#             return redirect('address_form')
#     else:
#         form = CustomerAddressForm()
#     return render(request, 'customer/address_form.html', {'form': form})


class ListAddressViewJson(AdminRequiredMixin, AjayDatatableView):
    model = CustomerAddress
    columns = ['street', 'city', 'state','zip_code', 'actions']
    exclude_from_search_columns = ['actions']
    extra_search_columns = ['street','zip_code']

    def get_initial_queryset(self):
        return self.model.objects.all()

    def render_column(self, row, column):
        if column == 'actions':
            edit_action = '<a href={} role="button" class="btn btn-warning btn-xs mr-1 text-white">Edit</a>'.format(
                reverse('address_edit', kwargs={'pk': row.pk}))
            delete_action = '<a href="javascript:;" class="remove_record btn btn-danger btn-xs" data-url={} role="button">Delete</a>'.format(
                reverse('address_delete', kwargs={'pk': row.pk}))
            return edit_action + delete_action
        else:
            return super(ListAddressViewJson, self).render_column(row, column)

class UpdateAddressView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = 'customer/address_form.html'
    # success_message = "Address updated successfully"
    success_url = reverse_lazy('address_form')


class AddressUpdateView(AdminRequiredMixin, LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomerAddress
    form_class = CustomerAddressForm
    template_name = 'customer/address_form.html'
    # success_message = "Address updated successfully"
    success_url = reverse_lazy('address_form')

class AddressDeleteView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = CustomerAddress

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)

class DeleteAddressView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = CustomerAddress

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        payload = {'delete': 'ok'}
        return JsonResponse(payload)


class AddressDeleteView(DeleteView):
    model = CustomerAddress
    template_name = 'address_confirm_delete.html'
    success_url = reverse_lazy('address_form')



class CreateContactView(CreateView):
    template_name = 'customer/contact.html'

    def get(self, request, *args, **kwargs):
        # fm = CustomerContactForm()
        # stud = CustomerContact.objects.all()
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        fm = CustomerContactForm(request.POST)
        if fm.is_valid():
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            reg = CustomerContact(name=name, email=email, subject=subject, message=message)
            reg.save()
            return redirect('website')

# class ContactView(TemplateView):
#     template_name = 'customer/contact.html'
#
#     def get(self, request, args, *kwargs):
#         form = CustomerContactForm()
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request, args, *kwargs):
#         form = CustomerContactForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('website')
#         return render(request, self.template_name, {'form': form})


class ListContactView(AdminRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'customer/contactus.html'
class ListContactViewJson(AdminRequiredMixin, AjayDatatableView):
    model = CustomerContact
    columns = ['name', 'email', 'subject','message']
    extra_search_columns = ['name','email']

    def get_initial_queryset(self):
        return self.model.objects.all()

    def render_column(self, row, column):
        return super(ListContactViewJson, self).render_column(row, column)


