# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from accounts.models import AnconUser

def recursiveChildren(node, level=0):
    results = [{'id': node['id'], 'level': level, 'name': node['data']['name']}]
    if node.get('children', 0) and len(node.get('children')) > 0:
        for child in node['children']:
            results.extend(recursiveChildren(child, level=level + 1))
    return results


def check_ajax_auth(any_views):
	"""
	Проверяет является запрос от аутентифицированного пользователя. 
	"""
	def wrapper(*args, **argv):
		req = args[0]
		sid = req.session.session_key

		# если сессионная переменная пуста или 
		if not sid:
			return HttpResponse('<h1>You not auth!</h1>', status=401)

		session = Session.objects.get(session_key=sid)
		session_data = session.get_decoded()
		uid = session_data.get('_auth_user_id')		
		print('uid=', uid)
		try:
			user = AnconUser.objects.get(pk=uid)
		except: 
			return HttpResponse('<h1>You not auth!</h1>', status=401)

		return any_views(*args, **argv)
		
	return wrapper