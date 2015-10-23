# -*- coding:utf-8 -*-

import json
from django.http import JsonResponse, HttpResponse
from index.models import City
from index.helpers import check_ajax_auth


@check_ajax_auth
def city_list(request):
    """
    Возвращает список городов полученных из базы в ввиде json.
    """
    cites = City.objects.all()
    your_data = []
    tmp_dict = {}
    for elem in cites:
        tmp_dict[elem.id] = elem.city_name
        #your_data.append(tmp_dict)

    #your_data = {key: value for (key, value) in cities}
    resp = json.dumps(tmp_dict, ensure_ascii=False)
    return JsonResponse(resp, safe=False)

def inx(request):
    return HttpResponse('<h1>Api it works!</h1>')
