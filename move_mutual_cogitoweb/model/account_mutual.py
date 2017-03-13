# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _

import pprint
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

	@api.multi
	def generate_cogito_mutual(self):
		# Duplica un record di account_mode lanciando super().copy() 
		# e tutte le account_move_line collegate.
		# Lancia una query per trovare le account_move_line collegate
		# e invertine le colonne date/avere
		# Impedisce di creare duplicati di duplicati

	   tot_records = len(self)
       	   processed_records = 0
           messages = ""
           for s in self:

               if s.ref == False:
                  # Se ref non e' definito, non posso cercare
                  messages += ("\nIl campo 'riferimento' non e' valido per il record %s" % s.id)

               # Se esiste gia un duplicato, ferma tutto
               reciproco_id = s.cerca_reciproco(s.id, s.ref)
               if reciproco_id != False:
                  messages += ("\nIl reciproco il record %s esiste già" % s.id)

               duplicato_id = super(cogito_account_mutual, s).copy(default={'name':"Storno " + s.ref, 'ref':"Storno " + s.ref})
               #duplicato_obj = self.env['account.move'].browse(duplicato_id)

               # ### Query update nome/riferimento
               #self.pool.get('account.move').write(self.env.cr, self.env.uid, [duplicato_id.id], {
               #   'name':"Storno " + s.ref,
               #   'ref':"Storno " + s.ref
               #})
               #_logger.info(pprint.pformat(duplicato_id))
               #duplicato_id.name = "Storno " + s.ref
               #duplicato_id.ref = "Storno " + s.ref

               for row in duplicato_id.line_id:

                 debit_new = row.credit
                 credit_new = row.debit

                 row.write(
                    {
                        'debit': debit_new,
                        'credit': credit_new
                    }
                 )

               processed_records += 1

           return {
             'type': 'ir.actions.act_window.message',
             'title': _('Message'),
             'message': _("Created %s multual movements of %s moves selected" % (tot_records, processed_records)) + "\n\n" + messages,
             'close_button_title': _('Close'),
           }

