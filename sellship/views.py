

from django.shortcuts import render, redirect
from django.contrib import messages

from sellship.forms import EbayShippingInfoForm
from sellship.models import Item


# from sellship.models import ShipperChoices, AccountEbayChoices


# Create your views here.

def sendRegister_view(request):
    if request.method == 'POST':
        form = EbayShippingInfoForm(request.POST)
        if form.is_valid():
            shipping_info = form.save()
            # shipping_info.smart = smart_item
            # shipping_info.save()
            messages.success(request, 'Данные успешно сохранены!')
            return redirect('sendRegister')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EbayShippingInfoForm()
    
    context = {
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
