from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.shortcuts import render

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