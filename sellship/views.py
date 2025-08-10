

from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404

from sellship.forms import EbayShippingInfoForm
from sellship.models import Item
from sellship.models.shipping_info import EbayShippingInfo, StatusType, CountryChoices, ShipperChoices


# from sellship.models import ShipperChoices, AccountEbayChoices


# Create your views here.

def edit_shipping_item(request, item_id):
    shipping_item = get_object_or_404(EbayShippingInfo, pk=item_id)
    
    if request.method == 'POST':
        form = EbayShippingInfoForm(request.POST, instance=shipping_item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Запись #{item_id} успешно обновлена!')
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

def items_view(request):
    # Получаем параметры фильтрации из GET запроса
    country_filter = request.GET.get('country')
    shipper_filter = request.GET.get('shipper')
    marketplace_filter = request.GET.get('marketplace')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # Базовый QuerySet
    shipping_items = EbayShippingInfo.objects.all().select_related('smart')
    
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
    
    # Сортировка по приоритету (последнее обновление статуса)
    if priority_filter == 'high':
        shipping_items = shipping_items.order_by('-last_updated_status')
    elif priority_filter == 'medium':
        shipping_items = shipping_items.order_by('last_updated_status')
    elif priority_filter == 'low':
        shipping_items = shipping_items.order_by('last_updated_status')
    
    context = {
        'shipping_items': shipping_items,
        'countries': CountryChoices.choices,
        'shippers': ShipperChoices.choices,
        'statuses': StatusType.choices,
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
            shipping_info = form.save()
            # shipping_info.smart = smart_item
            # shipping_info.save()
            messages.success(request, 'Данные успешно сохранены!')
            return redirect('sendRegister')
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
