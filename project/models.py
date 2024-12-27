from django.db import models
# Create your models here.

class Item(models.Model):
    i_type = models.CharField(max_length=250, null=True, blank=True, unique=True)
    quantity = models.FloatField(null=True, blank=True)
    retailer_price = models.FloatField(null=True, blank=True)
    chef_price = models.FloatField(null=True, blank=True)
    bulk_price = models.FloatField(null=True, blank=True)
    gst = models.FloatField(null=True, blank=True)
    tsales = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.i_type} - {self.quantity} - {self.tsales}"

class Sale(models.Model):
    i_type = models.CharField(max_length=250, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    subtotal = models.FloatField(null=True, blank=True)
    gst_subtotal = models.FloatField(null=True, blank=True)
    sale_id = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=40, null=True, blank=True)
    customer_addrs = models.CharField(max_length=250, null=True, blank=True)
    customer_mobile = models.IntegerField(max_length=10, null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=[('paid', 'paid'), ('unpaid', 'unpaid'), ('return', 'return')], default='unpaid')
    discount = models.FloatField(null=True, blank=True)
    sale_price = models.FloatField(null=True, blank=True)
    return_status = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.sale_id} - {self.i_type} - {self.quantity}"
