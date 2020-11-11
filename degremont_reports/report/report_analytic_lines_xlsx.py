# Author: Julien Coux
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models
import logging
from datetime import date, datetime

_logger = logging.getLogger(__name__)

class AnalyticLinesXslx(models.AbstractModel):
    _name = 'report.report_analytic_lines_xlsx'
    _inherit = 'report.account_financial_report.abstract_report_xlsx'

    def __init__(self, pool, cr):
        # main sheet which will contains report
        # Formats
        self.proyect_header_format = None
        self.proyect_footer_format = None
        self.proyect_footer_format_amount = None
        self.departure_header_format = None
        self.departure_footer_format = None
        self.departure_footer_format_amount = None

    def _get_report_name(self, report):
        report_name = _('Analytic Lines')
        return self._get_report_complete_name(report, report_name)

    def _get_report_columns(self, report):
        if not report.group_by_account:
            res = {
                0: {'header': _('Proyect'),
                    'field': 'proyect_id',
                    'type': 'many2one',
                    'width': 30},
                1: {'header': _('Departure'),
                    'field': 'departure_id',
                    'type': 'many2one',
                    'width': 30},
                2: {'header': _('Date'),
                    'field': 'date',
                    'width': 30},
                3: {'header': _('Account'),
                    'field': 'account_id',
                    'type': 'many2one',
                    'width': 20},
                4: {'header': _('Invoice'),
                    'field': 'invoice_display_name',
                    'width': 20},
                5: {'header': _('Partner'),
                    'field': 'partner_id',
                    'type': 'many2one',
                    'width': 20},
                6: {'header': _('Description'),
                    'field': 'description',
                     'width': 30},
                7: {'header': _('Amount'),
                    'field': 'amount',
                    'type': 'amount',
                    'width': 14},
                    }
        else:
            res = {
                0: {'header': _('Proyect'),
                    'field': 'proyect_id',
                    'type': 'many2one',
                    'width': 30},
                1: {'header': _('Departure'),
                    'field': 'departure_id',
                    'type': 'many2one',
                    'width': 30},}
            count = len(res.keys())
            column = {count: {'header': _('Accumulated'),
                    'field': _('accumulated'),
                    'type': 'amount',
                    'width': 14},}
            res = {**res, **column}
            count+=1
            for child in report.child_ids:
                total = 0
                month=datetime.strptime(child.date_from,"%Y-%m-%d")
                month=month.strftime("%b-%Y")
                column = {count: {'header': _(month),
                    'field': _('period_balance'),
                    'type': 'amount',
                    'report_id': child.id,
                    'width': 14},}
                res = {**res, **column}
                count+=1
            column = {count: {'header': _('Amount'),
                'field': 'amount',
                'type': 'amount',
                'width': 14},
                }
            res = {**res, **column}
            count+=1
        return res

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 2

    def _get_report_filters(self, report):

        filters=[]
        filters.append([_('Date range filter'),
         _('Since: %s From: %s To: %s') % (report.date_since, report.date_from, report.date_to)])

        return filters

    def _generate_report_content(self, workbook, report):

        # Display array header for account lines
        self.write_array_header()
        self.proyect_header_format = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#fafafa'})
        self.proyect_footer_format = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#fbfbfb'})
        self.departure_header_format = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#eeeeee'})
        self.departure_footer_format = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#ededed'})
        self.proyect_footer_format_amount = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#fbfbfb'})
        self.departure_footer_format_amount = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#ededed'})
        self.proyect_header_format_amount = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#fafafa'})
        self.departure_header_format_amount = workbook.add_format(
            {'bold': True,
             'border': True,
             'bg_color': '#eeeeee'})
        currency_id = self.env['res.company']._get_user_currency()
        self.proyect_footer_format_amount.set_num_format(
            '#,##0.'+'0'*currency_id.decimal_places)
        self.departure_footer_format_amount.set_num_format(
            '#,##0.'+'0'*currency_id.decimal_places)
        self.proyect_header_format_amount.set_num_format(
            '#,##0.'+'0'*currency_id.decimal_places)
        self.departure_header_format_amount.set_num_format(
            '#,##0.'+'0'*currency_id.decimal_places)
        # For each account
        for proyect in report.proyect_ids:

                self.write_proyect_header(proyect, report)
                for departure in proyect.departure_ids:
                    self.write_departure_header(departure, proyect, report)
                    if not report.group_by_account:
                        for account in departure.account_ids:
                            self.write_line(account)
                            self.write_line_custom(account)
                        self.write_departure_footer(departure, report)
                if not report.group_by_account:
                    self.write_proyect_footer(proyect, report)

    def write_line_custom(self, line_object):
        row_pos=self.row_pos-1
        for col_pos, column in self.columns.items():
            if column.get('header',False) in _('Account'):
                value = line_object.account_id.code or ''
                value+='-'
                value+= line_object.account_id.name or ''
                self.sheet.write_string(
                    row_pos, col_pos, value, self.proyect_footer_format
                )
            if column.get('header',False) in _('Invoice'):
                value = line_object.invoice_id.display_name or ''
                self.sheet.write_string(
                    row_pos, col_pos, value, self.proyect_footer_format
                )


    def write_proyect_header(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """

        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            self.sheet.write_string(
                self.row_pos, col_pos, '', self.proyect_header_format)
            if column.get('header',False) in _('Proyect'):
                value = line_object.name or ''
                self.sheet.write_string(
                    self.row_pos, col_pos, value, self.proyect_header_format)
            if report.group_by_account:
                if column.get('header',False) in _('Accumulated'):
                    value = line_object.accumulated or 0.0
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.proyect_header_format_amount
                    )
                self.write_month_proyect(line_object, report, col_pos, column)
                if column.get('header',False) in _('Amount'):
                    value = line_object.total
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.proyect_header_format_amount
                    )
        self.row_pos+=1

    def write_departure_header(self, line_object, proyect, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """


        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            self.sheet.write_string(
                self.row_pos, col_pos, '', self.departure_header_format)
            if column.get('header',False) in _('Departure'):
                value = line_object.name or ''
                self.sheet.write_string(
                    self.row_pos, col_pos, value, self.departure_header_format)
            if report.group_by_account:
                if column.get('header',False) in _('Accumulated'):
                    value = line_object.accumulated or 0.0
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.departure_header_format_amount
                    )
                self.write_month_departure(line_object, proyect, report, col_pos, column)
                if column.get('header',False) in _('Amount'):
                    value = line_object.total
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.departure_header_format_amount
                    )
        self.row_pos+=1

    def write_proyect_footer(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """


        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            self.sheet.write_string(
                self.row_pos, col_pos, '', self.proyect_footer_format)
            if column.get('header',False) in _('Amount'):
                value = line_object.amount or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.proyect_footer_format_amount
                )
            if column.get('header',False) in _('Description'):
                value = 'Total'
                self.sheet.write_string(
                    self.row_pos, col_pos, value, self.proyect_footer_format
                )
        self.row_pos+=2

    def write_departure_footer(self, line_object, report):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """


        cell_format = self.format_amount
        for col_pos, column in self.columns.items():
            self.sheet.write_string(
                self.row_pos, col_pos, '', self.departure_footer_format)
            if column.get('header',False) in _('Amount'):
                value = line_object.amount or 0.0
                self.sheet.write_number(
                    self.row_pos, col_pos, float(value), self.departure_footer_format_amount
                )
            if column.get('header',False) in _('Description'):
                value = 'Subtotal'
                self.sheet.write_string(
                    self.row_pos, col_pos, value, self.departure_footer_format
                )
        self.row_pos+=1

    def write_month_departure(self, line_object, proyect, report, col_pos, column):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        
        for month in report.child_ids:
            if line_object.name:
                if column.get('report_id',False) and column['report_id'] == month.id:
                    value= report.get_month_departure(month, line_object, proyect)
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.departure_header_format_amount
                    )
    
    def write_month_proyect(self, line_object, report, col_pos, column):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        
        for month in report.child_ids:
            if line_object.name:
                if column.get('report_id',False) and column['report_id'] == month.id:
                    value= report.get_month_proyect(month, line_object)
                    self.sheet.write_number(
                        self.row_pos, col_pos, float(value), self.proyect_header_format_amount
                    )
