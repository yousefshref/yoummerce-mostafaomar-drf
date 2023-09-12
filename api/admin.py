from django.contrib import admin
from . import models
from django.db.models import Sum
from django.db.models import Q
from rangefilter.filters import DateRangeFilterBuilder
from django.contrib.auth.models import Group
from django.utils.html import format_html



class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 3


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'buy_price', 'total_buy_price', 'sell_price', 'total_sell_price', 'before_disc', 'commission','earning', 'total_earning',
                    'stock', 'add_stock', 'remove_stock', 'date',)

    list_editable = ('buy_price', 'sell_price', 'before_disc', 'commission', 'stock',
                     'add_stock', 'remove_stock',)

    search_fields = ('title', 'stock',)
    # search = ("title",)

    inlines = [ProductImageInline]

    change_list_template = 'product/change_list.html'


    def sum_of_buy_price(self):
        product_model = models.Product.objects.all()
        buy_price_sum = product_model.aggregate(Sum('total_buy_price'))[
            'total_buy_price__sum']
        return buy_price_sum

    def sum_of_sell_price(self):
        product_model = models.Product.objects.all()
        sell_price_sum = product_model.aggregate(Sum('total_sell_price'))[
            'total_sell_price__sum']
        return sell_price_sum

    def sum_of_earning(self):
        product_model = models.Product.objects.all()
        earning_sum = product_model.aggregate(Sum('total_earning'))[
            'total_earning__sum']
        return earning_sum


    def changelist_view(self, request, extra_context=None):

        my_context = {
            'earning_sum': self.sum_of_earning(),
            'buy_price_sum': self.sum_of_buy_price(),
            'sell_price_sum': self.sum_of_sell_price(),
        }

        return super(ProductAdmin, self).changelist_view(request,
                                                    extra_context=my_context)

class OrderItemInline(admin.TabularInline):
    fields = ('product', 'is_returned', 'quantity', 'order_item_sell_price', 'order_earning', 'order_ecommission')
    model = models.OrderItems
    extra = 1

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.fields = ('product', 'quantity', 'order_item_sell_price', 'order_ecommission',)
        return super().get_fields(request, obj)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'edited', 'note', 'get_list_display', 'is_arrived','discount','state')

    def edited(self, obj):
        items = models.OrderItems.objects.filter(order_item=obj.id)
        for item in items:
            if item.is_returned == True:
                return format_html('<span style="background:red;">edited</span>',)
            # break

    # def edited(self, obj):
    #     if obj.id == 158:
    #         return format_html('<span style="background:red;">edited</span>',)

    fields = ('user', 'name', 'address', 'phone', 'phone2', 'state', 'shipping', 'is_arrived', 'discount', 'note', 'total_order', 'total_earning', 'total_commission',)


    list_editable = ('is_arrived','state','discount',)
    search_fields = ('user__username', 'name', 'address','total_order',)
    actions = ("arrived", "ontheway","pending","parted","mortaga3","cancel")
    list_filter = (
        ("date", DateRangeFilterBuilder()),
        'is_arrived'
    )

    inlines = [OrderItemInline]

    # delete earning from fiekds if not superuser
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('id','edited','user', 'name', 'address', 'phone', 'phone2', 'is_arrived', 'state', 'discount', 'note', 'total_order', 'shipping', 'total_earning', 'total_commission', 'date',)

        if not request.user.is_superuser:
            return ('id','edited','user', 'name', 'address', 'phone', 'phone2', 'is_arrived', 'state', 'discount', 'note', 'total_order', 'shipping', 'total_commission', 'date',)

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.fields = ('user', 'name', 'address', 'phone', 'phone2', 'state', 'shipping', 'is_arrived', 'discount', 'note', 'total_order', 'shipping', 'total_commission',)
        return super().get_fields(request, obj)


    change_list_template = 'order/change_list.html'

    # actions
    @admin.action(description='لاغي')
    def cancel(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=10)
            obj.save()


    @admin.action(description='مرتجع')
    def mortaga3(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=9)
            obj.save()


    @admin.action(description='تسليم جزئي')
    def parted(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=8)
            obj.save()


    @admin.action(description='تسليم ناجح')
    def arrived(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=6)
            obj.save()

    @admin.action(description='قيد الشحن')
    def ontheway(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=5)
            obj.save()

    @admin.action(description='قيد المراجعة')
    def pending(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=4)
            obj.save()


    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        queryset = models.Order.objects.all()

        if request.GET.get('date__range__gte') and request.GET.get('date__range__lte'):
            queryset = models.Order.objects.filter(date__range=[request.GET.get('date__range__gte'), request.GET.get('date__range__lte')])


        if request.GET.get('q'):
            queryset = models.Order.objects.filter(Q(user__username__icontains=request.GET.get('q')) | Q(name__icontains=request.GET.get('q')) | Q(address__icontains=request.GET.get('q')) | Q(total_order__icontains=request.GET.get('q')))

            
        if request.GET.get('is_arrived__id__exact'):
            queryset = models.Order.objects.filter(is_arrived=request.GET.get('is_arrived__id__exact'))


        if request.GET.get('q') and request.GET.get('date__range__gte') and request.GET.get('date__range__lte'):
            queryset = models.Order.objects.filter(date__range=[request.GET.get('date__range__gte'), request.GET.get('date__range__lte')]).filter(Q(user__username__icontains=request.GET.get('q')) | Q(name__icontains=request.GET.get('q')) | Q(address__icontains=request.GET.get('q')) | Q(total_order__icontains=request.GET.get('q')))


        if request.GET.get('q') and request.GET.get('is_arrived__id__exact'):
            queryset = models.Order.objects.filter(is_arrived=request.GET.get('is_arrived__id__exact')).filter(Q(user__username__icontains=request.GET.get('q')) | Q(name__icontains=request.GET.get('q')) | Q(address__icontains=request.GET.get('q')) | Q(total_order__icontains=request.GET.get('q')))


        if request.GET.get('date__range__gte') and request.GET.get('date__range__lte') and request.GET.get('is_arrived__id__exact'):
            queryset = models.Order.objects.filter(date__range=[request.GET.get('date__range__gte'), request.GET.get('date__range__lte')]).filter(is_arrived=request.GET.get('is_arrived__id__exact'))

            
        if request.GET.get('date__range__gte') and request.GET.get('date__range__lte') and request.GET.get('is_arrived__id__exact') and request.GET.get('q'):
            queryset = models.Order.objects.filter(date__range=[request.GET.get('date__range__gte'), request.GET.get('date__range__lte')]).filter(Q(user__username__icontains=request.GET.get('q')) | Q(name__icontains=request.GET.get('q')) | Q(address__icontains=request.GET.get('q')) | Q(total_order__icontains=request.GET.get('q'))).filter(is_arrived=request.GET.get('is_arrived__id__exact'))



        order_sum = queryset.aggregate(Sum('total_order'))[
            'total_order__sum']
        
        earning_sum = queryset.aggregate(Sum('total_earning'))[
            'total_earning__sum']
        
        commission_sum = queryset.aggregate(Sum('total_commission'))[
            'total_commission__sum']
        
        if not request.user.is_superuser:
            my_context = {
                'earning_sum': 0,
                'order_sum': 0,
                'commission_sum': 0,
            }
        else:
            my_context = {
                'earning_sum': earning_sum,
                'order_sum': order_sum,
                'commission_sum': commission_sum,
            }

        return super(OrderAdmin, self).changelist_view(request,
                                                    extra_context=my_context)


class StateAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'shipping',)

    list_editable = ('name', 'shipping',)



admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.State, StateAdmin)
admin.site.register(models.Category)
admin.site.register(models.Shipped)
admin.site.register(models.Cart)


admin.site.unregister(Group)
