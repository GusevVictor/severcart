from django.shortcuts import render

def main_summary(request):
	"""
	"""
	context = {}
	return render(request, 'reports/main_summary.html', context)
