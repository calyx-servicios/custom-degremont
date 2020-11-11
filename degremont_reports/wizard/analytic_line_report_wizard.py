# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# Copyright 2017 Akretion - Alexis de Lattre
# Copyright 2018 Eficent Business and IT Consuting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from datetime import date
from datetime import  timedelta
import time
import datetime

import logging
_logger = logging.getLogger(__name__)

class AnalyticLineReportWizard(models.TransientModel):
    """Trial balance report wizard."""

    _name = "analytic.line.report.wizard"
    _description = "Analytic Line Report Wizard"
    @api.model
    def get_first_day(self):
        return date(date.today().year, 1, 1)

    @api.model
    def get_account_types(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        account_type_ids = literal_eval(ICPSudo.get_param('account_degremont.account_type_ids', default='False'))
        if account_type_ids:
            return self.env['account.account.type'].search([('id','in',account_type_ids)]).ids

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date range'
    )
    date_since = fields.Date(required=True, default=get_first_day)

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    account_type_ids = fields.Many2many(
        comodel_name='account.account.type',
        string='Filtrar por tipos de cuenta',
        relation='analytic_line_report_wizard_type_ids',
        default=get_account_types
    )

    filter_type_ids = fields.Many2many(
        comodel_name='account.account.type',
        string='Filtrar por tipos de cuenta',
        default=get_account_types
    )

  

    group_by_account = fields.Boolean(string='Group by Account',default=True)

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        required=False,
        string='Company'
    )

    def mkDateTime(self, dateString,strFormat="%Y-%m-%d"):
        # Expects "YYYY-MM-DD" string
        # returns a datetime object
        eSeconds = time.mktime(time.strptime(dateString,strFormat))
        return datetime.datetime.fromtimestamp(eSeconds)

    @api.onchange('date_range_id')
    def onchange_date_range_id(self):
        """Handle date range change."""
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end
        if self.date_from:
            _date=self.mkDateTime(self.date_from)
            self.date_since=date(_date.year, 1, 1)

    @api.multi
    def _check(self):
        if self.date_since <= self.date_from and self.date_from <= self.date_to:
            return True
        raise UserError('Dates are incorrect. Verify this rule: Initial <= From <= To')

    @api.multi
    def button_export_tree(self):
        self.ensure_one()
        self._check()
        model = self.env['report_analytic_lines']
        report = model.create(self._prepare_report_analytic_lines())
        report.compute_data_for_report()
        view_id = self.env.ref('degremont_reports.report_analytic_lines_account_tree').id
        return {
            'name': _('Analytic Lines Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'report_analytic_lines_account',
            'view_mode': 'tree',
            'view_id': view_id,
            'limit': 5000,
            # 'domain': [('id', 'in', report.account_ids._ids)],
        }

    @api.multi
    def _prepare_report_analytic_lines(self):
        self.ensure_one()
        _logger.debug('=====>%s %s' % (self, self.account_type_ids.ids))
        res ={
            'date_from': self.date_from,
            'date_to': self.date_to,
            'date_since': self.date_since,
            'filter_account_type_ids': [(6, 0, self.account_type_ids.ids)],
            'group_by_account': self.group_by_account,
            'company_id': self.company_id.id,
        }
        _logger.debug('=====>%s' % (res))
        return res

    ################
    @api.multi
    def button_export_html(self):
        self.ensure_one()
        self._check()
        model = self.env['report_analytic_lines']
        report = model.create(self._prepare_report_analytic_lines())
        report.compute_data_for_report()
        action = self.env.ref(
            'degremont_reports.action_report_analytic_lines_html')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_pdf(self):
        self.ensure_one()
        self._check()
        model = self.env['report_analytic_lines']
        report = model.create(self._prepare_report_analytic_lines())
        report.compute_data_for_report()
        action = self.env.ref(
            'degremont_reports.action_report_analytic_lines_qweb')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        self._check()
        model = self.env['report_analytic_lines']
        report = model.create(self._prepare_report_analytic_lines())
        report.compute_data_for_report()
        action = self.env.ref(
            'degremont_reports.action_report_analytic_lines_xlsx')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        context1['active_id'] = report.id
        context1['active_ids'] = report.ids
        vals['context'] = context1
        return vals
