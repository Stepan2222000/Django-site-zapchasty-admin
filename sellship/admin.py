from django.contrib import admin
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from .models import Item, Brand, TransportType
from sellship.models import Item, EbayShippingInfo



class SpaceSeparatedArrayField(SimpleArrayField):   # Класс который позволит нам указывать парочку элементов через пробел
    def prepare_value(self, value):
        if isinstance(value, list):
            return ' '.join(str(v) for v in value)
        return value

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.strip().split()]


# Формочка для админки под модель Item, чтобы перезаписать некоторые поля которые по дефолту не подерживаються под Django, к примеру ArrayField
class ItemAdminForm(forms.ModelForm):
    brand = forms.MultipleChoiceField(
        choices=Brand.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    connect_brand = forms.MultipleChoiceField(
        choices=Brand.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    transport_type = forms.MultipleChoiceField(
        choices=TransportType.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    area_usage = SpaceSeparatedArrayField(forms.CharField(max_length=20), required=False)
    article = SpaceSeparatedArrayField(forms.CharField(max_length=20), required=False)
    connect_article = SpaceSeparatedArrayField(forms.CharField(max_length=20), required=False)

    class Meta:
        model = Item
        fields = '__all__'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemAdminForm
    list_display = ['id', 'name', 'originality']



@admin.register(EbayShippingInfo)
class EbayShippingInfoAdmin(admin.ModelAdmin):
    list_display = ["smart", "number_announcement"]