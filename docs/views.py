from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
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
        #
        pass
    elif request.method == 'GET':
        #
        form = AddDoc()
        context['form'] = form
    else:
        # метод не поддерживается
        pass
    return render(request, 'docs/delivery.html', context)
