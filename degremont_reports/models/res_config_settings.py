# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_type_ids= fields.Many2many(comodel_name='account.account.type',string='Account Types',)


    @api.model
    def get_values(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        account_type_ids = literal_eval(ICPSudo.get_param('account_degremont.account_type_ids', default='False'))
        res.update(
            account_type_ids=account_type_ids,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("account_degremont.account_type_ids", self.account_type_ids.ids)
