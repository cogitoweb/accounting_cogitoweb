# -*- coding: utf-8 -*-
{
	'name': "Odoo Cogito Move Mutual",
	'summary': "",
	'author': "CogitoWEB",
	'description': "Odoo Cogito move mutual",


	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
	# for the full list
	'category': 'Test',
	'version': '0.1',


	# any module necessary for this one to work correctly
	'depends': ['base', 'account'],


	# always loaded
	'data': [
        'view/account_mutual_view.xml',

		# 'security/ir.model.access.csv',
		# 'security/security.xml'
	],

	
	# only loaded in demonstration mode
	'demo': [
		# 'demo.xml',
	],


	'installable': True
}
