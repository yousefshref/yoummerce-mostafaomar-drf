from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Sum


class Category(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)

    def __str__(self):
        return str(self.name)

class Product(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=100, null=True, blank=True)
    buy_price = models.IntegerField(blank=True, null=True, default=0)
    total_buy_price = models.IntegerField(blank=True, null=True, default=0)
    sell_price = models.IntegerField(blank=True, null=True, default=0)
    total_sell_price = models.IntegerField(blank=True, null=True, default=0)
    before_disc = models.IntegerField(blank=True, null=True, default=0)
    earning = models.IntegerField(blank=True, null=True, default=0)
    total_earning = models.IntegerField(blank=True, null=True, default=0)
    commission = models.IntegerField(blank=True, null=True, default=0)
    stock = models.IntegerField(blank=True, null=True, default=0)
    add_stock = models.IntegerField(blank=True, null=True, default=0)
    remove_stock = models.IntegerField(blank=True, null=True, default=0)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    related_products = models.ManyToManyField('self', blank=True)
    date = models.DateField(auto_now_add=True,null=True, blank=True)

    def save(self, *args, **kwargs):

        self.total_buy_price = self.buy_price * self.stock
        self.total_sell_price = self.sell_price * self.stock
        self.total_earning = self.earning * self.stock

        super(Product, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.title) + ' ' + str(self.id)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    alt = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)

    def __str__(self):
        return str(self.product.title)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)

    total_price = models.IntegerField(null=True, blank=True, default=0)
    total_commission = models.IntegerField(null=True, blank=True, default=0)

    date = models.DateField(auto_now_add=True,null=True, blank=True)

    def save(self, *args, **kwargs):

        self.total_price = self.product.sell_price * self.quantity
        self.total_commission = self.product.commission * self.quantity

        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user) + " " + str(self.id)

class State(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    shipping = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name


class Shipped(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, db_index=True, unique=True)


    def __str__(self):
        return str(self.name)

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True, default=0)
    phone2 = models.CharField(max_length=500, null=True, blank=True, default=0)
    note = models.TextField(max_length=500, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE)
    shipping = models.IntegerField(null=True, blank=True, default=0)
    is_arrived = models.ForeignKey(Shipped, default=Shipped.objects.get(pk=4).pk, related_name='is_arrived', null=True, blank=True, on_delete=models.CASCADE)
    discount = models.IntegerField(null=True, blank=True, default=0)
    total_order = models.IntegerField(null=True, blank=True, default=0)
    total_earning = models.IntegerField(null=True, blank=True, default=0)
    total_commission = models.IntegerField(null=True, blank=True, default=0)
    date = models.DateField(auto_now_add=True,null=True, blank=True)

    def save(self, *args, **kwargs):
        order_items = OrderItems.objects.filter(order_item=self.id)

        self.shipping = State.objects.get(name=self.state.name).shipping

        if(self.discount is not 0):
            self.total_order = order_items.aggregate(Sum('order_item_sell_price'))['order_item_sell_price__sum'] + self.discount
            self.total_earning = order_items.aggregate(Sum('order_earning'))['order_earning__sum'] + self.discount
        else:
            self.total_order = order_items.aggregate(Sum('order_item_sell_price'))['order_item_sell_price__sum']
            self.total_earning = order_items.aggregate(Sum('order_earning'))['order_earning__sum']

        self.total_commission = order_items.aggregate(Sum('order_ecommission'))['order_ecommission__sum']

        if self.is_arrived.pk == 10:
            for order_item in order_items:
                order_item.quantity = 0
                order_item.save()
                # order_item.save_base()

            self.total_order = 0
            self.state.shipping = 0
            self.total_earning = 0
            self.total_commission = 0
            self.shipping = 0


        if self.is_arrived.pk == 9:
            for order_item in order_items:
                order_item.quantity = 0
                order_item.save()
                # order_item.save_base()

            self.total_order = -abs(self.state.shipping)
            self.total_earning = -abs(self.state.shipping)
            self.state.shipping = 0
            self.total_commission = 0
            self.shipping = 0


        # returned
        returned_items = OrderItems.objects.filter(order_item=self.pk, is_returned=True)

        if self.is_arrived.pk == 8 and returned_items:
            self.total_order = self.total_order - returned_items.aggregate(Sum('order_item_sell_price'))['order_item_sell_price__sum']
            self.total_earning = self.total_earning - returned_items.aggregate(Sum('order_earning'))['order_earning__sum']
            self.total_commission = self.total_commission - returned_items.aggregate(Sum('order_ecommission'))['order_ecommission__sum']


        try:
            self.total_order = self.total_order + self.state.shipping
        except:
            print('aaaa')

        super(Order, self).save(*args, **kwargs)

        # auto delete if there's no order items


    def delete(self, *args, **kwargs):
        order_items = OrderItems.objects.filter(order_item=self.id)

        self.total_order = order_items.aggregate(Sum('order_item_sell_price'))['order_item_sell_price__sum']
        self.total_earning = order_items.aggregate(Sum('order_earning'))['order_earning__sum']
        self.total_commission = order_items.aggregate(Sum('order_ecommission'))['order_ecommission__sum']

        super(OrderItems, self).delete(*args, **kwargs)



    def __str__(self):
        return str(self.name) + ' ' + str(self.id)

# {
# "user":1,
# "name":"dass",
# "address":"111a",
# "phone":11131,
# "address":"111a",
# "state":2
# }


class MyException(Exception):
    pass

class OrderItems(models.Model):
    order_item = models.ForeignKey(Order, related_name='order_item', null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)

    is_returned = models.BooleanField(default=False, null=True, blank=True)

    order_item_sell_price = models.IntegerField(null=True, blank=True)
    order_earning = models.IntegerField(null=True, blank=True)
    order_ecommission = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # check if the stock will be under 0
        if self.product.stock - self.quantity > -1:
            try:
                old_quantity = OrderItems.objects.get(id=self.id).quantity
                new_quantity = self.quantity
                diff = new_quantity - old_quantity
                self.product.stock = self.product.stock -+ diff
                self.order_item_sell_price = self.product.sell_price * self.quantity
                self.order_earning = self.product.earning * self.quantity
                self.order_ecommission = self.product.commission * self.quantity
                self.product.save()
            except OrderItems.DoesNotExist:
                old_quantity = 0
                new_quantity = self.quantity
                diff = new_quantity - old_quantity
                self.product.stock = self.product.stock -+ diff
                self.order_item_sell_price = self.product.sell_price * self.quantity
                self.order_earning = self.product.earning * self.quantity
                self.order_ecommission = self.product.commission * self.quantity
                self.product.save()
        else:
            raise MyException('No Enough Stock')


        super(OrderItems, self).save(*args, **kwargs)

        if self.order_item_id:
            self.order_item.save()

        # returned
        # order = Order.objects.get(id=self.order_item.pk)
        # if self.is_returned == True:
        #     order.is_arrived = Shipped.objects.get(id=8)
        #     order.save()




    def delete(self, *args, **kwargs):
        self.product.stock = self.product.stock + self.quantity
        self.product.save()

        super(OrderItems, self).delete(*args, **kwargs)

        if self.order_item_id:
            self.order_item.save()


    def __str__(self):
        return str(self.product.title)


# {
# "order_item":21,
# "product":3,
# "quantity":3
# }


@receiver(pre_save, sender=Product)
def calculate_earning(sender, instance, **kwargs):
    instance.earning = instance.sell_price - instance.buy_price

    if instance.add_stock is not 0:
        instance.stock = instance.stock + instance.add_stock
        instance.add_stock = 0

    if instance.remove_stock is not 0:
        instance.stock = instance.stock - instance.remove_stock
        instance.remove_stock = 0
