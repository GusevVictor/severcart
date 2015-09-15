from django.shortcuts import render
from django.http import HttpResponseRedirect
from index.forms.add_cartridge_type import AddCartridgeType
from index.models import CartridgeType

# Create your views here.
def index(request):

    return render(request, 'index/index.html', {})


def add_cartridge_type(request):

    if request.method == 'POST':
        form_obj = AddCartridgeType(request.POST)
        if form_obj.is_valid():
            # добавляем новый тип расходного материала
            form_obj.save()
            return HttpResponseRedirect(request.path)

    else:
        form_obj = AddCartridgeType()
        all_types = CartridgeType.objects.all()
    return render(request, 'index/add_type.html', {'form' : form_obj, 'types' : all_types})

def add_cartridge_item(request):
    pass
