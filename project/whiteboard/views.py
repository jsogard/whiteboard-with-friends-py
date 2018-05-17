from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import User, Board, Scheme
import re

sanitaryPattern = re.compile('^[a-zA-Z0-9_-]+$')

testBoards = \
[\
	{\
		'scheme_id': 	1,	\
		'owner': 	'owner0',	\
		'scheme': 	'feather',	\
	 	'id':		7,			\
	},\
	{\
		'scheme_id': 	2,	\
		'owner': 	'owner1',	\
		'scheme': 	'sakura',	\
	 	'id':		73,			\
	},\
	{\
		'scheme_id': 	3,	\
		'owner': 	'owner2',	\
		'scheme': 	'cloudy',	\
	 	'id':		8,			\
	},\
	{\
		'scheme_id': 	4,	\
		'owner': 	'owner3',	\
		'scheme': 	'xv',	\
	 	'id':		1,			\
	},\
	{\
		'scheme_id': 	5,	\
		'owner': 	'owner4',	\
		'scheme': 	'escheresque',	\
	 	'id':		4,			\
	},\
	{\
		'scheme_id': 	6,	\
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
	
	scheme = None
	for board in testBoards:
		if board['id'] == id:
			return render(request, 'whiteboard.html', { 'scheme': Scheme.objects.get(id=board['scheme_id']) })
	
	return None

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
	
	return render(request, 'gallery.html', getBoards())

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
	
	return render(request, 'gallery.html', getBoards(owner=user))

'''
url: n/a
private use method
returns boards with attached scheme peeks
'''
def getBoards(owner=None):
	schemes = Scheme.objects.all()
	boardData = []
	for board in testBoards:
		b = board.copy()
		b['frame'] = schemes.get(id=b['scheme_id']).frame
		b['border'] = schemes.get(id=b['scheme_id']).border
		boardData.append(b)
		
	data = { 'boards': boardData }
	if owner != None:
		data['user'] = owner
	
	return data