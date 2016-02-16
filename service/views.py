from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.helpers import is_admin

@login_required
@is_admin
def submenu(request):
    """
    """
    return render(request, 'service/submenu.html', context={})
