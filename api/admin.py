from django.contrib import admin
from . import models
from django.db.models import Sum
from django.db.models import Q
from rangefilter.filters import DateRangeFilterBuilder
from django.contrib.auth.models import Group


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 3


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'buy_price', 'sell_price', 'before_disc', 'earning', 'commission',
                    'stock', 'add_stock', 'remove_stock', 'date',)
    list_editable = ('buy_price', 'sell_price', 'before_disc', 'commission', 'stock',
                     'add_stock', 'remove_stock',)
    inlines = [ProductImageInline]


class OrderItemInline(admin.TabularInline):
    fields = ('product', 'quantity', 'order_item_sell_price', 'order_earning', 'order_ecommission')
    model = models.OrderItems
    extra = 1

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.fields = ('product', 'quantity', 'order_item_sell_price', 'order_ecommission',)
        return super().get_fields(request, obj)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_arrived',)
                    
    fields = ('user', 'name', 'address', 'phone', 'notes', 'state', 'shipping', 'is_arrived', 'discount', 'total_order', 'total_earning', 'total_commission',)
    
        
    list_editable = ('is_arrived',)
    search_fields = ('user__username', 'name', 'address')
    actions = ("arrived", "ontheway","pending",)
    list_filter = (
        ("date", DateRangeFilterBuilder()),
        'is_arrived'
    )

    inlines = [OrderItemInline]

    # delete earning from fiekds if not superuser
    def get_list_display(self, request):
        if request.user.is_superuser:
            return self.list_display + ('id','user', 'name', 'address', 'phone', 'state', 'shipping', 'total_order', 'total_earning', 'total_commission', 'date',)

        if not request.user.is_superuser:
            return self.list_display + ('id','user', 'name', 'address', 'phone', 'state', 'shipping',
                    'is_arrived', 'total_order', 'total_commission', 'date',)

    def get_fields(self, request, obj=None):
        if not request.user.is_superuser:
            self.fields = ('user', 'name', 'address', 'phone', 'notes', 'state', 'shipping', 'is_arrived', 'discount', 'total_order', 'total_commission',)
        return super().get_fields(request, obj)
    

    change_list_template = 'order/change_list.html'

    # actions
    @admin.action(description='arrived')
    def arrived(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=1)
            obj.save()

    @admin.action(description='on the way')
    def ontheway(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=2)
            obj.save()
            
    @admin.action(description='pending')
    def pending(modeladmin, request, queryset):
        for obj in queryset:
            obj.is_arrived = models.Shipped.objects.get(id=3)
            obj.save()


    # sums
    def sum_of_order(self):
        order_model = models.Order.objects.all()
        order_sum = order_model.aggregate(Sum('total_order'))[
            'total_order__sum']
        return order_sum

    def sum_of_earning(self):
        order_model = models.Order.objects.all()
        earning_sum = order_model.aggregate(Sum('total_earning'))[
            'total_earning__sum']
        return earning_sum

    def sum_of_commission(self):
        order_model = models.Order.objects.all()
        commission_sum = order_model.aggregate(Sum('total_commission'))[
            'total_commission__sum']
        return commission_sum

    def changelist_view(self, request, extra_context=None):
        if not request.user.is_superuser:
            my_context = {
                'earning_sum': 0,
                'order_sum': 0,
                'commission_sum': 0,
            }
        else:
            my_context = {
                'earning_sum': self.sum_of_earning(),
                'order_sum': self.sum_of_order(),
                'commission_sum': self.sum_of_commission(),
            }


        # check if there is a search
        if request.GET.get('q'):
            searched_objects = models.Order.objects.filter(
                Q(user__username__icontains=request.GET.get('q')) |
                Q(name__icontains=request.GET.get('q')) |
                Q(address__icontains=request.GET.get('q'))
            )
            order_sum = searched_objects.aggregate(Sum('total_order'))[
                'total_order__sum']
            earning_sum = searched_objects.aggregate(Sum('total_earning'))[
                'total_earning__sum']
            commission_sum = searched_objects.aggregate(Sum('total_commission'))[
                'total_commission__sum']
            my_context.update({
                'earning_sum': earning_sum,
                'order_sum': order_sum,
                'commission_sum': commission_sum,
            })

            if request.GET.get('date__range__gte') and request.GET.get('date__range__lte'):
                start_date = request.GET.get('date__range__gte')
                end_date = request.GET.get('date__range__lte')

                filtered_objects = searched_objects.filter(date__range=(start_date, end_date))

                order_sum = filtered_objects.aggregate(Sum('total_order'))[
                    'total_order__sum']
                earning_sum = filtered_objects.aggregate(Sum('total_earning'))[
                    'total_earning__sum']
                commission_sum = filtered_objects.aggregate(Sum('total_commission'))[
                    'total_commission__sum']
                my_context.update({
                    'earning_sum': earning_sum,
                    'order_sum': order_sum,
                    'commission_sum': commission_sum,
                })

                return super(OrderAdmin, self).changelist_view(request,
                                                            extra_context=my_context)
                                                            
            if request.GET.get('is_arrived__id__exact'):
                arrived = request.GET.get('is_arrived__id__exact')

                filtered_objects = searched_objects.filter(is_arrived=arrived)

                order_sum = filtered_objects.aggregate(Sum('total_order'))[
                    'total_order__sum']
                earning_sum = filtered_objects.aggregate(Sum('total_earning'))[
                    'total_earning__sum']
                commission_sum = filtered_objects.aggregate(Sum('total_commission'))[
                    'total_commission__sum']
                my_context.update({
                    'earning_sum': earning_sum,
                    'order_sum': order_sum,
                    'commission_sum': commission_sum,
                })

                return super(OrderAdmin, self).changelist_view(request,
                                                            extra_context=my_context)

            else:
                return super(OrderAdmin, self).changelist_view(request,
                                                            extra_context=my_context)
                                                            
        if request.GET.get('date__range__gte') and request.GET.get('date__range__lte'):
            start_date = request.GET.get('date__range__gte')
            end_date = request.GET.get('date__range__lte')

            filtered_objects = models.Order.objects.filter(date__range=(start_date, end_date))

            order_sum = filtered_objects.aggregate(Sum('total_order'))[
                'total_order__sum']
            earning_sum = filtered_objects.aggregate(Sum('total_earning'))[
                'total_earning__sum']
            commission_sum = filtered_objects.aggregate(Sum('total_commission'))[
                'total_commission__sum']
            my_context.update({
                'earning_sum': earning_sum,
                'order_sum': order_sum,
                'commission_sum': commission_sum,
            })

            return super(OrderAdmin, self).changelist_view(request,
                                                            extra_context=my_context)

        if request.GET.get('is_arrived__id__exact'):
            arrived = request.GET.get('is_arrived__id__exact')

            filtered_objects = models.Order.objects.filter(is_arrived=arrived)
            order_sum = filtered_objects.aggregate(Sum('total_order'))[
                'total_order__sum']
            earning_sum = filtered_objects.aggregate(Sum('total_earning'))[
                'total_earning__sum']
            commission_sum = filtered_objects.aggregate(Sum('total_commission'))[
                'total_commission__sum']
            my_context.update({
                'earning_sum': earning_sum,
                'order_sum': order_sum,
                'commission_sum': commission_sum,
            })

            return super(OrderAdmin, self).changelist_view(request,
                                                        extra_context=my_context)
            

        return super(OrderAdmin, self).changelist_view(request,
                                                    extra_context=my_context)





admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.State)
admin.site.register(models.Category)
admin.site.register(models.Shipped)
admin.site.register(models.Cart)


admin.site.unregister(Group)
