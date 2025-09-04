from django.db.models.expressions import RawSQL
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from sellship.models import Item


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