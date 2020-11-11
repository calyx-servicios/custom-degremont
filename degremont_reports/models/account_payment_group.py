##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import logging
_logger = logging.getLogger(__name__)


class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    @api.multi
    def post(self):
        context = self._context
        _logger.info('payment post========%s' % context)
        if not context.get('create_from_expense'):
            if not self.debt_move_line_ids:
                raise ValidationError(_(
                        'You can not confirm a payment group without debt lines!'))
        return super(AccountPaymentGroup, self).post()
    
    
    def _compute_name(self):
        
        for rec in self:
            _logger.info('computting name for payment group =====DEGREMONT===%s' % rec.id)
            if rec.state == 'cancel':
                name= _('Draft Payment')
                if rec.document_number and rec.document_type_id:
                    name = ("%s%s" % (
                        rec.document_type_id.doc_code_prefix or '',
                        rec.document_number))
                rec.name = name
            else:
                super(AccountPaymentGroup, self)._compute_name()


