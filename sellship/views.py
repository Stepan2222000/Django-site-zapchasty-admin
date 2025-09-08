

from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import models

from sellship.forms import EbayShippingInfoForm
from sellship.models.shipping_info import EbayShippingInfo, StatusType, CountryChoices, ShipperChoices, PriorityChoices


# from sellship.models import ShipperChoices, AccountEbayChoices


# Create your views here.

def edit_shipping_item(request, pk):
    shipping_item = get_object_or_404(EbayShippingInfo, pk=pk)
    
    if request.method == 'POST':
        form = EbayShippingInfoForm(request.POST, instance=shipping_item)
        if form.is_valid():
            # Создаем экземпляр формы, но не сохраняем
            updated_item = form.save(commit=False)
            
            # Если статус "Написал" или "Оффер", устанавливаем значения по умолчанию для необязательных полей
            if updated_item.status in ['НАПИСАЛИ', 'ОФФЕР']:
                if not updated_item.final_price:
                    updated_item.final_price = 0
                if not updated_item.overhead:
                    updated_item.overhead = 0
                if not updated_item.track_number:
                    updated_item.track_number = ''
                if not updated_item.seller_name:
                    updated_item.seller_name = ''
                if not updated_item.order_link:
                    updated_item.order_link = ''
            
            updated_item.save()
            messages.success(request, f'Запись #{pk} успешно обновлена!')
            return redirect('items')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EbayShippingInfoForm(instance=shipping_item)
    
    context = {
        'form': form,
        'shipping_item': shipping_item,
        'is_edit': True
    }
    return render(request, 'sendRegister.html', context)

def delete_shipping_item(request, item_id):
    shipping_item = get_object_or_404(EbayShippingInfo, pk=item_id)
    
    if request.method == 'POST':
        shipping_item.delete()
        messages.success(request, f'Запись #{item_id} успешно удалена!')
        return redirect('items')
    
    context = {
        'shipping_item': shipping_item
    }
    return render(request, 'confirm_delete.html', context)

def index_view(request):
    return redirect('/sellship/items/')

def items_view(request):
    # Получаем параметры фильтрации из GET запроса
    country_filter = request.GET.get('country')
    shipper_filter = request.GET.get('shipper')
    marketplace_filter = request.GET.get('marketplace')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # Базовый QuerySet
    # НЕЛЬЗЯ делать select_related('smart'): ItemFDW живёт в другой БД (parts_admin)
    # и Django не поддерживает cross-DB join. Оставляем ленивую загрузку по FK.
    shipping_items = EbayShippingInfo.objects.all()
    
    # Применяем фильтры
    if country_filter:
        shipping_items = shipping_items.filter(country=country_filter)
    if shipper_filter:
        shipping_items = shipping_items.filter(shipper=shipper_filter)
    if marketplace_filter:
        # Пока у нас только Ebay, можем добавить логику позже
        pass
    if status_filter:
        shipping_items = shipping_items.filter(status=status_filter)
    
    # Сортировка по приоритету
    if priority_filter == 'high':
        shipping_items = shipping_items.filter(priority='high')
    elif priority_filter == 'medium':
        shipping_items = shipping_items.filter(priority='medium')
    elif priority_filter == 'low':
        shipping_items = shipping_items.filter(priority='low')
    
    # Сортировка по приоритету (high -> medium -> low)
    priority_order = models.Case(
        models.When(priority='high', then=models.Value(1)),
        models.When(priority='medium', then=models.Value(2)),
        models.When(priority='low', then=models.Value(3)),
        default=models.Value(4),
        output_field=models.IntegerField(),
    )
    shipping_items = shipping_items.order_by(priority_order, '-last_updated_status')
    
    context = {
        'shipping_items': shipping_items,
        'countries': CountryChoices.choices,
        'shippers': ShipperChoices.choices,
        'statuses': StatusType.choices,
        'priorities': PriorityChoices.choices,
        'current_filters': {
            'country': country_filter,
            'shipper': shipper_filter,
            'marketplace': marketplace_filter,
            'status': status_filter,
            'priority': priority_filter,
        }
    }
    return render(request, 'items.html', context)

def sendRegister_view(request):
    if request.method == 'POST':
        form = EbayShippingInfoForm(request.POST)
        if form.is_valid():
            # Создаем экземпляр формы, но не сохраняем
            shipping_info = form.save(commit=False)
            
            # Если статус "Написал" или "Оффер", устанавливаем значения по умолчанию для необязательных полей
            if shipping_info.status in ['НАПИСАЛИ', 'ОФФЕР']:
                if not shipping_info.final_price:
                    shipping_info.final_price = 0
                if not shipping_info.overhead:
                    shipping_info.overhead = 0
                if not shipping_info.track_number:
                    shipping_info.track_number = ''
                if not shipping_info.seller_name:
                    shipping_info.seller_name = ''
                if not shipping_info.order_link:
                    shipping_info.order_link = ''
            
            shipping_info.save()
            messages.success(request, 'Данные успешно сохранены!')
            return redirect('items')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EbayShippingInfoForm()
    
    context = {
        'form': form
    }
    return render(request, 'sendRegister.html', context=context)

def sendRegisterEbay_view(request):
    if not request.method == "POST":
        return redirect("/sellship/sendRegister")

    announcemenet_number = request.POST.get("announcemenet_number")
    article = request.POST.get("article")
    country = request.POST.get("country")
    max_price = request.POST.get("max_price")


    pass

def sendRegisterOtherSites_view(request):
    pass
