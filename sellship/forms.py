from django import forms
from django.core.exceptions import ValidationError
from .models import EbayShippingInfo, CountryChoices, ItemFDW
from .models.shipping_info import ShipperChoices, ShippingType, AccountEbayChoices


class EbayShippingInfoForm(forms.ModelForm):
    smart = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'id': 'autoArticleComplete',
                'placeholder': 'Начни вводить артикул...',
                'class': 'smart-input',
                'autocomplete': 'off'
            }
        ),
        error_messages={
            'required': 'Поле "Артикул" обязательно для заполнения.',
        }
    )

    priority = forms.ChoiceField(
        choices=[
            ('low', 'Низкий'),
            ('medium', 'Средний'),
            ('high', 'Высокий'),
        ],
        initial='low',
        widget=forms.Select(
            attrs={
                'class': 'priority-select'
            }
        ),
        required=False
    )

    date_arrive = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'дата прихода на склад'
            }
        ),
        required=False
    )

    final_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'type': 'text',
                'placeholder': 'цена покупки с учетом доставки',
                'step': '0.01',
                'data-pattern': '^[0-9]{12}$'
            }
        ),
        required=False
    )

    seller_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'placeholder': 'имя продавца',
            }
        )
    )

    number_announcement = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'type': 'text',
                'placeholder': 'Введите номер объявления',
                'min': '100000000000',
                'max': '999999999999',
                'data-pattern': '^[0-9]{12}$'
            }
        ),
        required=False
    )

    max_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                'type': 'text',
                'placeholder': 'Максимальная цена покупки',
                'step': '0.01',
                'data-pattern': '^[0-9]{12}$'
            }
        ),
        required=False
    )

    track_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'трек номер',
                'minlength': '5'
            }
        ),
        required=False
    )

    comments = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'cols': 40
        }),
        required=False
    )

    overhead = forms.FloatField(
        initial=0,
        widget=forms.NumberInput(
            attrs={
                'type': 'text',
                'placeholder': 'Дополнительные затраты',
                'step': '0.01',
                'data-pattern': '^[0-9]{12}$'
            }
        ),
        required=False
    )


    class Meta:
        model = EbayShippingInfo
        fields = "__all__"

    def clean_smart(self):
        raw_value = self.cleaned_data.get('smart', '')
        if raw_value is None:
            raise ValidationError('Поле "Артикул" обязательно для заполнения.')

        value = str(raw_value).strip()

        # Try to extract ID if value looks like "<id> | ..."
        if '|' in value:
            value = value.split('|', 1)[0].strip()

        # Try lookup by primary key (smart id)
        item = ItemFDW.objects.filter(id=value).first()
        if item:
            return item

        raise ValidationError('Товар с таким артикулом не найден.')