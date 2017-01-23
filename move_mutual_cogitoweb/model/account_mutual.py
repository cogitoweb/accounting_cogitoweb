# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)


class cogito_account_mutual(models.Model):
	_inherit = 'account.move'


	def cerca_reciproco(self, search_id, search_ref):
		# Cerca altri record che hanno il campo "riferimento" (ref)
		# in comune con il record attuale. Non include se stesso.
		# Restituisce l'ID oppure False.

		# "bonifica" stringa
		search_ref = search_ref.replace("Storno ", "")

		query_search = """
				SELECT * FROM account_move
				WHERE ref LIKE '%%%s%%' AND id <> '%d'
			""" % (search_ref, search_id)

		self.env.cr.execute(query_search)
		query_result = self.env.cr.dictfetchall()
		num_result = len(query_result)

		if num_result == 1:
			return int(query_result[0]['id'])
		else:
			# Gestisce il caso in cui non esista un duplicato 
			# o se per errore ne esitono piu di uno
			return False




	@api.multi
	def visit_cogito_mutual(self):
		# Cerca il reciproco e produce un redirect
		# Se il reciproco non esiste, avvisa e non fare nulla

		if self.ref == False:
			# Se ref non e' definito, non posso cercare
			# o duplicare. Ferma tutto!
			raise exceptions.ValidationError("Il campo 'riferimento' non e' valido.")

		reciproco_id = self.cerca_reciproco(self.id, self.ref)

		if reciproco_id != False:
			# Se duplicato esiste, reindirizza
			return {
				'type' :     'ir.actions.act_window',
				'target':    'current',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'account.move',
				'res_id':    reciproco_id
			}
		else:
			# Se duplicato non esiste, avvisa
			raise exceptions.ValidationError("Non esiste un reciproco")




	@api.one
	def generate_cogito_mutual(self, default={}, context=None, *args, **kwargs):
		# Duplica un record di account_mode lanciando super().copy() 
		# e tutte le account_move_line collegate.
		# Lancia una query per trovare le account_move_line collegate
		# e invertine le colonne date/avere
		# Impedisce di creare duplicati di duplicati

		if not default:
			default = {}

		if self.ref == False:
			# Se ref non e' definito, non posso cercare
			# o duplicare. Ferma tutto!
			raise exceptions.ValidationError("Il campo 'riferimento' non e' valido.")

		# Se esiste gia un duplicato, ferma tutto
		reciproco_id = self.cerca_reciproco(self.id, self.ref)
		if reciproco_id != False:
			raise exceptions.ValidationError("Il reciproco esiste gia'")


		# copy(cr, uid, id, default=None, context=None)
		# Duplicate record with given id updating it with default values

		# cr -- database cursor
		# uid -- current user id
		# id -- id of the record to copy
		# default (dictionary) -- dictionary of field values to override in the original values of the copied record, e.g: {'field_name': overriden_value, ...}
		# context (dictionary) -- context arguments, like lang, time zone
		duplicato = super(cogito_account_mutual, self).copy(default, context=context)


		# ### ID del nuovo record
		reciproco_id = int(duplicato)
		_logger.info('<><><> EHI, duplicato con ID %d', (reciproco_id))


		# ### Query update nome/riferimento
		ref_new = "Storno " + self.ref
		name_new = "Storno " + self.ref
		query_update = """
				UPDATE account_move
				SET name = '%s', ref = '%s'
				WHERE id = %d
			""" % (name_new, ref_new, reciproco_id)

		self.env.cr.execute(query_update)



		# ### Query cerca account_move_line
		query_search = """
				SELECT id, debit, credit, move_id 
				FROM account_move_line WHERE move_id = %d
			""" % (reciproco_id)

		self.env.cr.execute(query_search)
		query_result = self.env.cr.dictfetchall()
		num_result = len(query_result)
		
		for row in range(0, num_result):
			line_id = query_result[row]['id']
			debit_new = query_result[row]['credit']
			credit_new = query_result[row]['debit']

			query_update = """
					UPDATE account_move_line
					SET debit = %s, credit = %s 
					WHERE id = %s
				""" % (debit_new, credit_new, line_id)

			# ### Query di scambio colonne
			self.env.cr.execute(query_update)



		_logger.info('<><><> EHI, generate_cogito_mutual ha terminato')
		return duplicato
