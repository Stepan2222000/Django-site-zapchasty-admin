from django import forms
from .models import EbayShippingInfo, CountryChoices


class EbayShippingInfoForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=CountryChoices.choices,
        required=True
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

    final_price = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'цена покупки с учетом доставки'
            }
        ),
        required=False
    )

    class Meta:
        model = EbayShippingInfo
        fields = '__all__'

        # widgets = {
        #     'last_updated_status': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        #     'date_arrive': forms.DateInput(attrs={'type': 'date'}),
        #     'date_list_create': forms.DateInput(attrs={'type': 'date'}),
        #     'comments': forms.Textarea(attrs={'rows': 3}),
        # }

        widgets = {
            'number_announcement': forms.NumberInput(attrs={
                'placeholder': 'Введите номер объявления',
                'type': "number"
            }),
            'max_price': forms.NumberInput(attrs={
                'placeholder': 'Максимальная цена покупки',
                'type': "number"
            }),
            'track_number': forms.TextInput(attrs={
                'placeholder': 'трек номер',
                'minlength': '5'
            }),
        }

        labels = {
            'number_announcement': 'Номер объявления',
            'smart': 'Товар (smart)',
            'max_price': 'Максимальная цена',
            'account_ebay': 'Аккаунт eBay',
            'status': 'Статус',
            'last_updated_status': 'Последнее обновление статуса',
            'seller_name': 'Имя продавца',
            'shipping_type': 'Тип доставки',
            'final_price': 'Финальная цена',
            'overhead': 'Дополнительные затраты',
            'shipper': 'Отправщик',
            'track_number': 'Трек-номер',
            'date_arrive': 'Дата прихода на склад',
            'country': 'Страна склада',
            'comments': 'Комментарий',
            'order_link': 'Ссылка на заказ',
            'rf_send': 'Отправлено в РФ',
            'date_list_create': 'Дата создания листа',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].initial = 'США'
