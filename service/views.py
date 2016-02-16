from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def submenu(request):
	"""
	"""
	return render(request, 'service/submenu.html', context={})
