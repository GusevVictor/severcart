# -*- coding:utf-8 -*-

from django.http import JsonResponse, HttpResponse
from index.models import City
from index.helpers import check_ajax_auth


@check_ajax_auth
def city_list(request):
    """Возвращает список городов полученных из базы в ввиде json.
    """
    cites = City.objects.all()
    your_data = []
    tmp_dict = {}
    for elem in cites:
        tmp_dict[elem.id] = elem.city_name

    return JsonResponse(tmp_dict, safe=False)


def inx(request):
    return HttpResponse('<h1>Api it works!</h1>')
