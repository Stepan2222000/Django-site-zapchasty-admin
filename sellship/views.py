import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db import models, DatabaseError, OperationalError
from django.db.models import Q
from django.db.models.expressions import RawSQL

from sellship.forms import EbayShippingInfoForm
from sellship.models.shipping_info import EbayShippingInfo, StatusType, CountryChoices, ShipperChoices, PriorityChoices
from sellship.models.item_fdw import ItemFDW

logger = logging.getLogger(__name__)


def safe_fdw_article_search(search_query: str) -> tuple[list, bool]:
    """
    Безопасный поиск по артикулу в ItemFDW (ArrayField).
    Возвращает (список ID, успех). При ошибке FDW возвращает ([], False).
    """
    if not search_query:
        return ([], True)

    try:
        matching_items = ItemFDW.objects.annotate(
            match=RawSQL(
                'EXISTS (SELECT 1 FROM unnest("артикул") AS a WHERE a ILIKE %s)',
                [f'%{search_query}%']
            )
        ).filter(match=True).values_list('id', flat=True)
        return (list(matching_items), True)
    except (DatabaseError, OperationalError) as e:
        logger.warning(f"FDW article search failed: {e}")
        return ([], False)
    except Exception as e:
        logger.error(f"Unexpected error in FDW search: {e}")
        return ([], False)


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

    # Получаем параметры поиска
    search_query = request.GET.get('search', '').strip()
    search_type = request.GET.get('search_type', 'all')

    # Базовый QuerySet
    shipping_items = EbayShippingInfo.objects.all()

    # Применяем фильтры
    if country_filter:
        shipping_items = shipping_items.filter(country=country_filter)
    if shipper_filter:
        shipping_items = shipping_items.filter(shipper=shipper_filter)
    if marketplace_filter:
        pass
    if status_filter:
        shipping_items = shipping_items.filter(status=status_filter)

    # Фильтр по приоритету
    if priority_filter == 'high':
        shipping_items = shipping_items.filter(priority='high')
    elif priority_filter == 'medium':
        shipping_items = shipping_items.filter(priority='medium')
    elif priority_filter == 'low':
        shipping_items = shipping_items.filter(priority='low')

    # Применяем поиск с обработкой ошибок FDW
    fdw_search_failed = False

    if search_query:
        if search_type == 'article':
            matching_items_list, fdw_success = safe_fdw_article_search(search_query)
            if fdw_success:
                shipping_items = shipping_items.filter(smart_id__in=matching_items_list)
            else:
                fdw_search_failed = True
                shipping_items = shipping_items.none()

        elif search_type == 'announcement':
            shipping_items = shipping_items.filter(
                number_announcement__icontains=search_query
            )

        elif search_type == 'track':
            shipping_items = shipping_items.filter(
                track_number__icontains=search_query
            )

        else:  # 'all'
            local_conditions = (
                Q(number_announcement__icontains=search_query) |
                Q(track_number__icontains=search_query)
            )
            matching_items_list, fdw_success = safe_fdw_article_search(search_query)

            if fdw_success and matching_items_list:
                shipping_items = shipping_items.filter(
                    Q(smart_id__in=matching_items_list) | local_conditions
                )
            else:
                if not fdw_success:
                    fdw_search_failed = True
                shipping_items = shipping_items.filter(local_conditions)

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
        },
        'search_query': search_query,
        'search_type': search_type,
        'fdw_search_failed': fdw_search_failed,
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
