from django.db.models.expressions import RawSQL
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from sellship.models import Item
from sellship.models.shipping_info import EbayShippingInfo


# Create your views here.


def articles_view(request):
    query = request.GET.get('q')

    if query and query.startswith("smart"):
        item = Item.objects.filter(id=query).first()
        if item:
            return JsonResponse([{
                "id": query
            }], safe=False)


    if query:
        items = Item.objects.annotate(
            match=RawSQL(
                "EXISTS (SELECT 1 FROM unnest(артикул) AS a WHERE a ILIKE %s)",
                [f"%{query}%"]
            )
        ).filter(match=True)
    else:
        items = Item.objects.all()

    result = []
    for item in items:
        matched_article = None
        priority = 99

        if query:
            for article in item.article:
                lower = article.lower()
                q = query.lower()

                if lower == q:
                    matched_article = article
                    priority = 0
                    break
                elif lower.startswith(q):
                    matched_article = article
                    priority = 1
                elif q in lower and priority > 2:
                    matched_article = article
                    priority = 2
        else:
            matched_article = item.article[0] if item.article else None
            priority = 0

        if matched_article:  # только если есть подходящий артикул
            result.append({
                "id": item.id,
                "similar_article": matched_article,
                "priority": priority
            })

    # Сортировка по приоритету и обрезка до 5 лучших
    sorted_result = sorted(result, key=lambda x: x["priority"])[:5]

    # Удалим поле "priority" перед отправкой
    for item in sorted_result:
        item.pop("priority")

    return JsonResponse(sorted_result, safe=False)


@csrf_exempt
def validate_item_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST is allowed')

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    # Разрешаем валидировать только subset полей, которые пришли
    # Создаём экземпляр без сохранения и валидируем только переданные поля
    item_field_names = {f.name for f in Item._meta.get_fields() if hasattr(f, 'attname')}

    # Оставляем только известные поля модели
    data = {k: v for k, v in payload.items() if k in item_field_names}

    item = Item()
    for field_name, value in data.items():
        setattr(item, field_name, value)

    # Исключаем все поля, которых нет во входных данных — чтобы не срабатывали проверки required
    exclude_fields = [name for name in item_field_names if name not in data]

    try:
        # validate_unique=False, так как мы не создаём запись и не проверяем уникальность по БД
        item.full_clean(exclude=exclude_fields, validate_unique=False)
        return JsonResponse({"valid": True, "errors": {}})
    except Exception as exc:
        # Собираем ошибки в удобный формат
        if hasattr(exc, 'message_dict'):
            errors = exc.message_dict
        else:
            errors = {"non_field_errors": [str(exc)]}
        return JsonResponse({"valid": False, "errors": errors}, status=400)


def get_db_column_mapping(model_class):
    """
    Создает маппинг db_column -> field_name для модели.
    Если db_column не указан, используется имя поля.
    """
    mapping = {}
    for field in model_class._meta.get_fields():
        if hasattr(field, 'attname'):
            db_column = getattr(field, 'db_column', None) or field.name
            mapping[db_column] = field.name
    return mapping


@csrf_exempt
def validate_all_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST is allowed')

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    # Получаем маппинги db_column -> field_name для обеих моделей
    item_db_mapping = get_db_column_mapping(Item)
    shipping_db_mapping = get_db_column_mapping(EbayShippingInfo)
    
    # Получаем все возможные db_column имена для фильтрации
    item_db_columns = set(item_db_mapping.keys())
    shipping_db_columns = set(shipping_db_mapping.keys())
    
    # Разделяем поля по моделям, используя db_column
    item_data = {}
    shipping_data = {}
    
    for db_column, value in payload.items():
        if db_column in item_db_columns:
            field_name = item_db_mapping[db_column]
            item_data[field_name] = value
        elif db_column in shipping_db_columns:
            field_name = shipping_db_mapping[db_column]
            shipping_data[field_name] = value
    
    all_errors = {}
    
    # Валидация Item
    if item_data:
        item = Item()
        for field_name, value in item_data.items():
            setattr(item, field_name, value)
        
        # Получаем все имена полей модели Item для исключения
        item_field_names = {f.name for f in Item._meta.get_fields() if hasattr(f, 'attname')}
        exclude_item_fields = [name for name in item_field_names if name not in item_data]
        
        try:
            item.full_clean(exclude=exclude_item_fields, validate_unique=False)
        except Exception as exc:
            if hasattr(exc, 'message_dict'):
                # Преобразуем ошибки обратно к db_column для ответа
                for field_name, errors in exc.message_dict.items():
                    # Находим соответствующий db_column для field_name
                    db_column = None
                    for db_col, f_name in item_db_mapping.items():
                        if f_name == field_name:
                            db_column = db_col
                            break
                    error_key = f"item_{db_column}" if db_column else f"item_{field_name}"
                    all_errors[error_key] = errors
            else:
                all_errors["item_non_field_errors"] = [str(exc)]
    
    # Валидация EbayShippingInfo
    if shipping_data:
        shipping = EbayShippingInfo()
        for field_name, value in shipping_data.items():
            setattr(shipping, field_name, value)
        
        # Получаем все имена полей модели EbayShippingInfo для исключения
        shipping_field_names = {f.name for f in EbayShippingInfo._meta.get_fields() if hasattr(f, 'attname')}
        exclude_shipping_fields = [name for name in shipping_field_names if name not in shipping_data]
        
        try:
            shipping.full_clean(exclude=exclude_shipping_fields, validate_unique=False)
        except Exception as exc:
            if hasattr(exc, 'message_dict'):
                # Преобразуем ошибки обратно к db_column для ответа
                for field_name, errors in exc.message_dict.items():
                    # Находим соответствующий db_column для field_name
                    db_column = None
                    for db_col, f_name in shipping_db_mapping.items():
                        if f_name == field_name:
                            db_column = db_col
                            break
                    error_key = f"shipping_{db_column}" if db_column else f"shipping_{field_name}"
                    all_errors[error_key] = errors
            else:
                all_errors["shipping_non_field_errors"] = [str(exc)]
    
    # Проверяем связь между моделями, если есть поля для связи
    # Ищем поле smart в payload (может прийти как db_column)
    smart_value = None
    for db_column, value in payload.items():
        if db_column in ['smart'] or (db_column in shipping_db_mapping and shipping_db_mapping[db_column] == 'smart'):
            smart_value = value
            break
    
    if item_data and shipping_data and smart_value:
        # Проверяем что такой Item существует
        if smart_value and not Item.objects.filter(id=smart_value).exists():
            all_errors["shipping_smart"] = ["Указанный Item не существует"]
    
    if all_errors:
        return JsonResponse({"valid": False, "errors": all_errors}, status=400)
    else:
        return JsonResponse({"valid": True, "errors": {}})