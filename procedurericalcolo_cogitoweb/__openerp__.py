{
	'name' : 'Procedure di ricalcolo',
	'version' : '1.0',
	'author' : "Eriberto Momente'",
	'website' : 'http://www.cogitoweb.it/',
	'category' : 'Tools',
	'depends' : ['base'],
	'description' : 'Procedure di Ricalcolo',
	'data': [
        'cogito_procedurericalcolo.xml',
        'menu_items.xml',
    ],
    
    'qweb': ['static/src/xml/*.xml'],
	'installable': True
}