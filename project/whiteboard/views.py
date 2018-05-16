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

'''
url: n/a
method api
check if a user is currently logged in
determined by session dictionary
returns rendering of login screen if not logged in otherwise None 
'''
def check_login_status(request):
	if 'username' in request.session and request.session != None and request.session != '':
		return None
	return render(request, 'login.html', {})

'''
url: /whiteboard/login
method api
if user does not exist or password is incorrect return proper error
correct credentials lofs user info into session and redirects them
returns appropriate error message or redirect url
'''
def login(request):
	responseJson = {'redirect': '', 'username':'', 'password':''}

	username = request.POST['username']
	password = request.POST['password']
		
	
	try:
		# if user exists, check password and return
		# else throw exception and return proper error
		u = User.objects.get(username=username)
		
		# check if password is correct
		if u.password_hash != u.crypto(password=password):
			responseJson['password'] = 'password incorrect'
			return JsonResponse(responseJson)
		
		# add user information to session
		request.session['username'] = username
		request.session['user_id'] = u.id
		
		# if user has been redirected to login from elsewhere, set redirect url
		if 'redirect' in request.session:
			responseJson['redirect'] = request.session['redirect']
		else:
			responseJson['redirect'] = '/whiteboard';
			
	except User.DoesNotExist:
		responseJson['username'] = 'user doesn\'t exist'
	
	return JsonResponse(responseJson)
	
'''
url: /whiteboard/logout
method api
removes user information from session, logging them out
'''
def logout(request):
	del request.session['username']
	del request.session['user_id']
	return HttpResponse('logged out')

'''
url: /whiteboard/new/user
method api
validates signup 
returns appropriate error message or creates user and returns redirect url
'''
def new_user(request):
	responseJson = {'redirect': '', 'username':'', 'password':'', 'confirm':''}

	username = request.POST['username']
	password = request.POST['password']
	confirm = request.POST['confirm']

	# verify password, confirm password, and username
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
		
	# if username exists return error
	# otherwise create user with proper password hash
	try:
		User.objects.get(username=username)
		responseJson['username'] = 'username taken'
	except User.DoesNotExist:
		u = User.objects.create(username=username)
		u.password_hash = u.crypto(password=password)
		u.save()
		request.session['username'] = username
		request.session['user_id'] = u.id
		if 'redirect' in request.session:
			responseJson['redirect'] = request.session['redirect']
		else:
			responseJson['redirect'] = '/whiteboard'
			
	return JsonResponse(responseJson)
		
'''
url: /whiteboard/<str:user>/<int:board_id>
page api
redirect to login if user logged out
find board with id by user
render board page with correct scheme and info
'''
def board(request, owner, id):
	login_render = check_login_status(request)
	if login_render != None:
		request.session['redirect'] = '/whiteboard/' + owner + '/' + id
		return login_render
	
	return render(request, 'whiteboard.html', { 'scheme': colorSchemes['restaurant'] })

'''
url: /whiteboard/
page api
redirect to login if user logged out
returns gallery page with all boards with their scheme peeks and thumbnail paths
'''
def gallery(request):
	login_render = check_login_status(request)
	if login_render != None:
		request.session['redirect'] = '/whiteboard'
		return login_render
	
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData })

'''
url: /whiteboard/<str:user>
page api
redirect to login if user logged out
returns gallery page with only boards by user with their scheme peeks and thumbnail paths
'''
def user(request, user):
	login_render = check_login_status(request)
	if login_render != None:
		request.session['redirect'] = '/whiteboard/' + user
		return login_render
	
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = colorSchemes[b['scheme']]['frame']
		b['border'] = colorSchemes[b['scheme']]['border']
		boardData.append(b)
	return render(request, 'gallery.html', { 'boards': boardData, 'user': user })
