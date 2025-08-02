from django.shortcuts import render

from sellship.models import ShipperChoices, AccountEbayChoices


# Create your views here.

def sendRegister_view(request):
    context = {
        'shipper_choices': ShipperChoices.choices,
        'account_ebay_choices': AccountEbayChoices.choices
    }
    return render(request, 'sendRegister.html', context=context)
