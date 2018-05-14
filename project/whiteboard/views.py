from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import hashlib
import re

sanitaryPattern = re.compile('^[a-zA-Z0-9_-]$')

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


def login(request):
	return render(request, 'login.html', {})

def new_user(request):
	responseJson = {'username':None, 'password':None, 'confirm':None}

	username = request.POST['username']
	password = request.POST['password']
	confirm = request.POST['confirm']

	if len(password) < 8:
		responseJson['password'] = 'password must exceed 7 characters'

	if password != confirm:
		responseJson['confirm'] = 'password does not match'

	if len(username) < 3:
		responseJson['username'] = 'username must exceed 2 characters'
	elif sanitaryPattern.match(username) == None:
		responseJson['username'] = 'no special characters except - or _'
		
	if responseJson['username'] != None or \
		responseJson['password'] != None or \
		responseJson['confirm'] != None:
		return JsonResponse(responseJson)
		
	try:
		User.objects.get(username=username)
		responseJson['username'] = 'username taken'
		return JsonResponse(responseJson)
	except User.DoesNotExist:
		return JsonResponse(responseJson)
				
#				p_hash = hashlib.sha256()
#				p_hash.update(password.encode('UTF-8'))
#				u = User(username=username, password_hash=p_hash.hexdigest())
		
		
		
		
	

def board(request, owner, id):
	return render(request, 'whiteboard.html', { 'scheme': colorSchemes['restaurant'] })

def gallery(request):
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData })

def user(request, user):
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData, 'user': user })
