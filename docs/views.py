import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import SCDoc
from .forms.add_doc import AddDoc

class handbook(TemplateView):
    template_name = 'docs/handbook.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(handbook, self).dispatch(*args, **kwargs)


@login_required
def service(request):
    """Списки договоров на обслуживание
    """
    return HttpResponse('<h1>Договора обслуживания</h1>')


@login_required
def delivery(request):
    """Списки договоров на поставку расходников
    """
    context = {}
    docs = SCDoc.objects.filter(departament=request.user.departament).filter(doc_type=1)
    context['docs'] = docs
    if request.method == 'POST':
        form = AddDoc(request.POST)
        if form.is_valid():
            data_in_post = form.cleaned_data
            number = data_in_post.get('number','')
            title = data_in_post.get('title','')
            money = data_in_post.get('money','')
            firm = data_in_post.get('firm','')
            short_cont = data_in_post.get('short_cont','')
            date = data_in_post.get('date','')
            m1 = SCDoc(number = number,
                       date = date,
                       firm = firm,
                       title = title,
                       short_cont = short_cont,
                       money = money,
                       departament = request.user.departament,
                       doc_type = 1,
                       )
            m1.save()
            context['form'] = form    
            return HttpResponseRedirect(request.path)
        else:
            print('Form is INVALID valid!')
            context['form'] = form    
    elif request.method == 'GET':
        #
        form = AddDoc()
        context['form'] = form
    else:
        # метод не поддерживается
        pass
    return render(request, 'docs/delivery.html', context)
