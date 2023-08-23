from django.db import models
from application.custom_models import DateTimeModel
from apps.user.models import User

class Customer(DateTimeModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_user',null=True)
    first_name = models.CharField('Full Name', max_length=30, blank=True)
    phone_number = models.BigIntegerField(blank=True, null=True, unique=True)

    
    def __str__(self):
        return self.user.first_name

    def delete(self, using=None):
        if self.user:
            self.user.delete()
        super(Customer, self).delete(using)


class CustomerAddress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.customer.username} - {self.street}, {self.city}"

class CustomerContact(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.subject}"
