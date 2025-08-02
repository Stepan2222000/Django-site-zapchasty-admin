

from django.shortcuts import render, redirect

from sellship.forms import EbayShippingInfoForm
from sellship.models import ShipperChoices, AccountEbayChoices


# Create your views here.

def sendRegister_view(request):
    form = EbayShippingInfoForm()
    context = {
        'shipper_choices': ShipperChoices.choices,
        'account_ebay_choices': AccountEbayChoices.choices,
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
