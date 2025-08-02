from django.contrib import admin
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from .models import Item, Brand, TransportType
from sellship.models import Item

# Register your models here.


# Формочка для админки под модель Item, чтобы перезаписать некоторые поля которые по дефолту не подерживаються под Django, к примеру ArrayField
class ItemAdminForm(forms.ModelForm):
    brand = SimpleArrayField(forms.ChoiceField(choices=Brand.choices), required=False)
    connect_brand = SimpleArrayField(forms.ChoiceField(choices=Brand.choices), required=False)
    transport_type = SimpleArrayField(forms.ChoiceField(choices=TransportType.choices), required=False)
    area_usage = SimpleArrayField(forms.CharField(max_length=20), required=False)
    article = SimpleArrayField(forms.CharField(max_length=20), required=False)
    connect_article = SimpleArrayField(forms.CharField(max_length=20), required=False)

    class Meta:
        model = Item
        fields = '__all__'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = ItemAdminForm
    list_display = ['id', 'name', 'originality']