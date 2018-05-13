from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

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