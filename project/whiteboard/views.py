from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

colorSchemes = {\
		"feather":{\
			"background":	"#FFFDF8",\
			"frame":		"url(../static/upfeathers.png)",\
			"border":		"#EEE9DE",\
			"text":			"#1E1D1C",\
			"accent":		"#EEE9DE"\
		},\
		"sakura":{\
			"background":	"#FFF8F5",\
			"frame":		"url(../static/sakura.png)",\
			"border":		"#FFF7D7",\
			"text":			"#403936",\
			"accent":		"#DFC7BC"\
		},\
	}

def index(request):
	return render(request, 'whiteboard.html', { 'scheme': colorSchemes['sakura'] })