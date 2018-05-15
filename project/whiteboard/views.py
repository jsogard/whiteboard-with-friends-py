from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import User, Board
import re

sanitaryPattern = re.compile('^[a-zA-Z0-9_-]+$')

colorSchemes = {\
		"feather":{\
			"background":	"#FFFDF8",\
			"frame":		"url(/static/patterns/upfeathers.png)",\
			"border":		"#EEE9DE",\
			"text":			"#1E1D1C",\
			"accent":		"#EEE9DE"\
		},\
		"sakura":{\
			"background":	"#FFF8F5",\
			"frame":		"url(/static/patterns/sakura.png)",\
			"border":		"#FFF7D7",\
			"text":			"#403936",\
			"accent":		"#DFC7BC"\
		},\
		"cloudy":{\
			"background":	"url(/static/patterns/cloudy-day.png)",\
			"frame":		"#D8DEEC",\
			"border":		"#BDCFCE",\
			"text":			"#363B3B",\
			"accent":		"#ACB6B5"\
		},\
		"xv":{\
			"background":	"url(/static/patterns/xv.png)",\
			"frame":		"#EAEAEA",\
			"border":		"#CDCDCD",\
			"text":			"#585858",\
			"accent":		"#CDCDCD"\
		},\
		"escheresque":{\
			"background":	"url(/static/patterns/escheresque_dark.png)",\
			"frame":		"#656565",\
			"border":		"#4B4B4B",\
			"text":			"#E5E5E5",\
			"accent":		"#656565"\
		},\
		"restaurant":{\
			"background":	"url(/static/patterns/restaurant.png)",\
			"frame":		"#95CFCD",\
			"border":		"#75AFAD",\
			"text":			"#324B4A",\
			"accent":		"#75AFAD"\
		},\
	}

testBoards = \
[\
	{\
		'title': 	'feather',	\
		'owner': 	'owner0',	\
		'scheme': 	'feather',	\
	 	'id':		7,			\
	},\
	{\
		'title': 	'sakura',	\
		'owner': 	'owner1',	\
		'scheme': 	'sakura',	\
	 	'id':		73,			\
	},\
	{\
		'title': 	'cloud',	\
		'owner': 	'owner2',	\
		'scheme': 	'cloudy',	\
	 	'id':		8,			\
	},\
	{\
		'title': 	'xv',	\
		'owner': 	'owner3',	\
		'scheme': 	'xv',	\
	 	'id':		1,			\
	},\
	{\
		'title': 	'escher',	\
		'owner': 	'owner4',	\
		'scheme': 	'escheresque',	\
	 	'id':		4,			\
	},\
	{\
		'title': 	'restaurant',	\
		'owner': 	'owner5',	\
		'scheme': 	'restaurant',	\
	 	'id':		14,			\
	},\
]

## returns none if logged in, otherwise returns the login page
def check_login_status(request):
	if 'username' in request.session and request.session != None and request.session != '':
		return None
	return render(request, 'login.html', {})

def login(request):
	responseJson = {'username':'', 'password':''}

	username = request.POST['username']
	password = request.POST['password']
		
	try:
		u = User.objects.get(username=username)
		if u.password_hash != u.crypto(password=password):
			responseJson['password'] = 'username taken'
			return JsonResponse(responseJson)
		request.session['username'] = username
		request.session['user_id'] = u.id
		return HttpResponseRedirect('/whiteboard')
	except User.DoesNotExist:
		responseJson['username'] = 'user doesn\'t exist'
		return JsonResponse(responseJson)

def new_user(request):
	responseJson = {'username':'', 'password':'', 'confirm':''}

	username = request.POST['username']
	password = request.POST['password']
	confirm = request.POST['confirm']

	if len(password) < 5:
		responseJson['password'] = 'password must exceed 4 characters'

	if password != confirm:
		responseJson['confirm'] = 'password does not match'

	if len(username) < 3:
		responseJson['username'] = 'username must exceed 2 characters'
	elif sanitaryPattern.match(username) == None:
		responseJson['username'] = 'no special characters except - or _'
		
	if responseJson['username'] != '' or \
		responseJson['password'] != '' or \
		responseJson['confirm'] != '':
		return JsonResponse(responseJson)
		
	try:
		User.objects.get(username=username)
		responseJson['username'] = 'username taken'
		return JsonResponse(responseJson)
	except User.DoesNotExist:
		u = User.objects.create(username=username)
		u.password_hash = u.crypto(password=password)
		u.save()
		request.session['username'] = username
		request.session['user_id'] = u.id
		return HttpResponseRedirect('/whiteboard')
	return None
		
		
		
		
	

def board(request, owner, id):
	login_render = check_login_status(request)
	if login_render != None:
		return login_render
	
	return render(request, 'whiteboard.html', { 'scheme': colorSchemes['restaurant'] })

def gallery(request):
	login_render = check_login_status(request)
	if login_render != None:
		return login_render
	
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData })

def user(request, user):
	login_render = check_login_status(request)
	if login_render != None:
		return login_render
	
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData, 'user': user })
