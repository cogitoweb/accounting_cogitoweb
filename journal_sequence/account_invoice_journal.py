# -*- coding: utf-8 -*-
from openerp import models, fields, api


class cogito_account_journal(models.Model):
	_inherit = 'account.journal' 
	_order = 'sequence'

	sequence = fields.Integer('Sequence')

	_defaults = {
		'sequence': '20'
	}


