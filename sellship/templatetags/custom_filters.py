from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    return dictionary.get(key)

@register.filter
def is_list(value):
    """Проверить, является ли значение списком"""
    return isinstance(value, list)

@register.filter
def format_price(value):
    """Форматирует цену как целое число, убирая .0"""
    if value is None:
        return ''
    try:
        # Если значение является целым числом, возвращаем его как есть
        if float(value).is_integer():
            return int(float(value))
        # Иначе возвращаем с двумя знаками после запятой
        return f"{float(value):.2f}"
    except (ValueError, TypeError):
        return value 