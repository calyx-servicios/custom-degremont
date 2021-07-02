
from odoo import models, fields, api
from odoo.tools import float_is_zero
from datetime import  timedelta
import time
import datetime
from collections import OrderedDict
import logging
_logger = logging.getLogger(__name__)

class Analytic_line_Report(models.TransientModel):

    _name = 'report_analytic_lines'
    _inherit = 'account_financial_report_abstract'

    company_id = fields.Many2one('res.company', string='Company')

    date_from = fields.Date()
    date_to = fields.Date()
    date_since = fields.Date()
    group_by_account = fields.Boolean()
    filter_account_type_ids = fields.Many2many(comodel_name='account.account.type')

    proyect_ids = fields.One2many(
        comodel_name='report_analytic_lines_proyect',
        inverse_name='report_id'
    )
    account_ids = fields.One2many(
        comodel_name='report_analytic_lines_account',
        inverse_name='report_id'
    )
    parent_id = fields.Many2one(
        comodel_name='report_analytic_lines',
        ondelete='cascade',
        index=True
    )
    # Data fields, used to browse report data
    child_ids = fields.One2many(
        comodel_name='report_analytic_lines',
        inverse_name='parent_id'
    )

    def formatDate(self, dtDateTime,strFormat="%Y-%m-%d"):
        # format a datetime object as YYYY-MM-DD string and return
        return dtDateTime.strftime(strFormat)

    def mkDateTime(self, dateString,strFormat="%Y-%m-%d"):
        # Expects "YYYY-MM-DD" string
        # returns a datetime object
        eSeconds = time.mktime(time.strptime(dateString,strFormat))
        return datetime.datetime.fromtimestamp(eSeconds)

    def mkFirstOfMonth(self, dtDateTime):
        #what is the first day of the current month
        #format the year and month + 01 for the current datetime, then form it back
        #into a datetime object
        return self.mkDateTime(self.formatDate(dtDateTime,"%Y-%m-01"))

    def mkLastOfMonth(self, dtDateTime):
        if int(dtDateTime.strftime("%m"))==12:
            dYear = str(int(dtDateTime.strftime("%Y"))+1)
        else:
            dYear = dtDateTime.strftime("%Y")        #get the year
        dMonth = str(int(dtDateTime.strftime("%m"))%12+1)#get next month, watch rollover
        dDay = "1"                               #first day of next month
        nextMonth = self.mkDateTime("%s-%s-%s"%(dYear,dMonth,dDay))#make a datetime obj for 1st of next month
        delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
        return nextMonth - delta
    
    def _prepare_report_analytic_line_child(self, start, end):
        self.ensure_one()
        return {
            'date_from': start,
            'date_to': end,
            'date_since': self.date_since,
            'filter_account_type_ids': [(6, 0, self.filter_account_type_ids.ids)],
            'group_by_account': self.group_by_account,
            'company_id': self.company_id.id,
            'parent_id': self.id
        }

    def get_childs(self):
        _logger.debug('=======GET_CHILDS======%s' % (self.filter_account_type_ids.ids))
        start=datetime.datetime.strptime(self.date_from,"%Y-%m-%d")
        end=datetime.datetime.strptime(self.date_to, "%Y-%m-%d")
        _logger.debug('Start Day: %s' % start)
        _logger.debug('End Day: %s' % end)
        months=OrderedDict(((start + timedelta(_)).strftime(r"%m-%y"), None) for _ in range((end - start).days)).keys()
        _logger.debug(months)
        for month in months:
            _month=datetime.datetime.strptime(month, "%m-%y")
            first=self.mkFirstOfMonth(_month)
            last=self.mkLastOfMonth(_month)
            if first<start:
                first=start
            if last>end:
                last=end
            _logger.debug('month %s' % _month)
            _logger.debug('First Day: %s' % first)
            _logger.debug('Last Day: %s' % last)
            model = self.env['report_analytic_lines']
            report_child = model.create(self._prepare_report_analytic_line_child(first,last))
            report_child.compute_data_for_report()
    
    def _get_format_date_header(self, child_date):
        month=datetime.datetime.strptime(child_date,"%Y-%m-%d")
        month=month.strftime("%b-%Y")
        return month
    
    def get_month_proyect(self, child, proyect):
        month_proyect=self.env['report_analytic_lines_proyect'].search([
                        ('report_id','=',child.id),
                        ('name','=',proyect.name)])
        value = month_proyect.amount
        value = round(value, 2)
        return value
    
    def get_month_departure(self, child, departure, proyect):
        month_proyect=self.env['report_analytic_lines_proyect'].search([
                        ('report_id','=',child.id),
                        ('name','=',proyect.name)])
        month_departure=self.env['report_analytic_lines_departure'].search([
                        ('report_id','=',child.id),
                        ('proyect_id','=',month_proyect.id),
                        ('name','=',departure.name)])
        value = month_departure.amount
        value = round(value, 2)
        return value


        

class Analytic_line_Report_Proyect(models.TransientModel):
    _name = 'report_analytic_lines_proyect'
    _inherit = 'account_financial_report_abstract'

    _order = 'sequence'

    report_id = fields.Many2one(
        comodel_name='report_analytic_lines',
        ondelete='cascade',
        index=True
    )
    departure_ids = fields.One2many(
        comodel_name='report_analytic_lines_departure',
        inverse_name='proyect_id'
    )

    sequence = fields.Integer(index=True, default=1)


    # Data fields, used for report display

    name = fields.Char()


    amount = fields.Float(digits=(16, 2), string='Amount')
    accumulated = fields.Float(digits=(16, 2), string='Accumulated')
    @api.depends('amount', 'accumulated')
    def _compute_amount(self):
        for proyect in self:
            proyect.total = proyect.accumulated+proyect.amount

    total = fields.Float(digits=(16, 2), string='Amount', compute=_compute_amount)

    


class Analytic_line_Report_Departure(models.TransientModel):
    _name = 'report_analytic_lines_departure'
    _inherit = 'account_financial_report_abstract'
    _order = 'sequence'
    report_id = fields.Many2one(
        comodel_name='report_analytic_lines',
        ondelete='cascade',
        index=True
    )
    proyect_id = fields.Many2one(
        comodel_name='report_analytic_lines_proyect',
        ondelete='cascade',
        index=True
    )
    account_ids = fields.One2many(
        comodel_name='report_analytic_lines_account',
        inverse_name='departure_id'
    )
    sequence = fields.Integer(index=True, default=1)
    name = fields.Char()


    amount = fields.Float(digits=(16, 2), string='Amount')
    accumulated = fields.Float(digits=(16, 2), string='Accumulated')

    @api.depends('amount', 'accumulated')
    def _compute_amount(self):
        for department in self:
            department.total = department.accumulated+department.amount

    total = fields.Float(digits=(16, 2), string='Amount', compute=_compute_amount)

    
       

class Analytic_line_Report_Account(models.TransientModel):
    _name = 'report_analytic_lines_account'
    _inherit = 'account_financial_report_abstract'
    _order = 'sequence'

    report_id = fields.Many2one(
        comodel_name='report_analytic_lines',
        ondelete='cascade',
        index=True
    )
    proyect_id = fields.Many2one(
        comodel_name='report_analytic_lines_proyect',
        ondelete='cascade',
        index=True
    )
    departure_id = fields.Many2one(
        comodel_name='report_analytic_lines_departure',
        ondelete='cascade',
        index=True
    )
    sequence = fields.Integer(index=True, default=1)


    # Data fields, used for report display
    account_id = fields.Many2one(
        'account.account',
        index=True
    )
    proyect = fields.Char()
    departure = fields.Char()
    date = fields.Date()
    description = fields.Char()

    amount = fields.Float(digits=(16, 2), string='Amount')
    account_type_id = fields.Many2one('account.account.type')
    currency_id = fields.Many2one('res.currency')
    amount_currency = fields.Float(digits=(16, 2),string='Amount Currency')
    invoice_id = fields.Many2one('account.invoice')
    invoice_display_name = fields.Char()
    partner_id = fields.Many2one('res.partner')

class Analytic_line_ReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_analytic_lines'

    @api.multi
    def compute_data_for_report(self):
        self.ensure_one()
        _logger.debug('==compute_date====>%s' % (self.filter_account_type_ids) )
        self._inject_proyect_values(self.filter_account_type_ids, self.date_from, self.date_to)
        self._inject_departure_values(self.filter_account_type_ids, self.date_from, self.date_to)
        self._inject_account_values(self.filter_account_type_ids, self.date_from, self.date_to)
        if not self.parent_id:
            self.get_childs()
        return True
    
    def _query_common_block(self):
        query = """
            account_analytic_line  as aal
            join account_analytic_account as aaa on aal.account_id = aaa.id
            join account_account as aa on aal.general_account_id = aa.id
            left join account_move_line as aml on aml.id = aal.move_id
            left join account_invoice as ai on ai.id = aml.invoice_id
            left join res_partner as rp on aml.partner_id = rp.id
            """
        return query

    def _inject_account_values(self, filter_account_type_ids, date_from, date_to):
        query_inject_account = """
            INSERT INTO
                report_analytic_lines_account
                (
                report_id,
                create_uid,
                create_date,
                sequence,
                proyect,
                departure,
                account_id,
                date,
                invoice_id,
                partner_id,
                description,
                amount,
                account_type_id,
                currency_id,
                amount_currency,
                departure_id,
                proyect_id,
                invoice_display_name
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                ROW_NUMBER() OVER () as sequence,
                proyect,
                departure,
                account,
                date,
                invoice_id,
                partner_id,
                description,
                amount,
                account_type,
                currency,
                amount_currency,
                departure_id,
                proyect_id,
                display_name
            FROM (

            select aaa.code as proyect,
                    aaa.name as departure,
                    aa.id as account,
                    aal.date as date,
                    ai.id as invoice_id,
                    rp.id as partner_id,
                    aal.name as description,
                    aal.amount as amount,
                    aa.user_type_id as account_type,
                    aal.currency_id as currency,
                    aal.amount_currency as amount_currency,
                    0 as acumulado,
                    par.id as departure_id,
                    pr.id as proyect_id,
                    ai.document_number as display_name
            from """+self._query_common_block()+"""
                left outer join report_analytic_lines_proyect as pr on aaa.code=pr.name and pr.report_id =%s
                left outer join report_analytic_lines_departure as par on aaa.name=par.name and par.report_id =%s
                and pr.id=par.proyect_id
            where aa.user_type_id in %s and aal.date BETWEEN %s AND %s
            order by aal.date,aa.id
            ) as whatever
            """
        query_inject_account_params = (
            self.id,
            self.env.uid,
            self.id,
            self.id,
            filter_account_type_ids._ids,
            date_from,
            date_to,
        )
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _query_departure_block(self):
        query = """
            select 
                pr.id as proyect_id,
                aaa.code as proyect,
                aaa.name as departure,
                sum(aal.amount) as amount
            from account_analytic_line  as aal
                join account_analytic_account as aaa on aal.account_id = aaa.id
                join account_account as aa on aal.general_account_id = aa.id
                left join report_analytic_lines_proyect as pr on aaa.code=pr.name and pr.report_id=%s
            where aa.user_type_id in %s
            """
        return query

    def _inject_proyect_values(self, filter_account_type_ids, date_from, date_to):
        query_inject_account = """
            WITH accounts as (
                    select aaa.code as proyect,
                        sum(aal.amount) as amount
                from """+self._query_common_block()+"""
                where aa.user_type_id in %s and aal.date BETWEEN %s AND %s
                group by aaa.code
                order by aaa.code
            ),
            accumulated as (
                    select aaa.code as proyect,
                        sum(aal.amount) as amount
                from """+self._query_common_block()+"""
                where aa.user_type_id in %s and aal.date BETWEEN %s AND %s
                group by aaa.code
                order by aaa.code
            )
            INSERT INTO
                report_analytic_lines_proyect
                (
                report_id,
                create_uid,
                create_date,
                sequence,
                name,
                amount,
                accumulated
                )
            SELECT
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                ROW_NUMBER() OVER () as sequence,
                pro.proyect as name,
                pro.amount as amount,
                acc.amount as accumulated
            FROM 
                accounts as pro left outer join accumulated acc on
                pro.proyect=acc.proyect

        
            """
        query_inject_account_params = (
            filter_account_type_ids._ids,
            date_from,
            date_to,
            filter_account_type_ids._ids,
            self.date_since,
            date_from,
            self.id,
            self.env.uid
        )
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)

    def _inject_departure_values(self, filter_account_type_ids, date_from, date_to):
        query_inject_account = """
            WITH 
            departures as (
                """+self._query_departure_block()+"""
                and aal.date BETWEEN %s AND %s
                group by pr.id,aaa.code,aaa.name
                order by aaa.name
            ),
            accumulated as (
                """+self._query_departure_block()+"""
                and aal.date BETWEEN %s AND %s
                group by pr.id,aaa.code,aaa.name
                order by aaa.name
            )
            INSERT INTO
                report_analytic_lines_departure
                (
                report_id,
                create_uid,
                create_date,
                sequence,
                name,
                proyect_id,
                amount,
                accumulated
                )
            select
                %s AS report_id,
                %s AS create_uid,
                NOW() AS create_date,
                ROW_NUMBER() OVER () as sequence,
                dp.departure,
                dp.proyect_id,
                dp.amount as amount,
                ac.amount as accumulated
            From departures dp left outer join accumulated as ac
                on dp.proyect=ac.proyect and dp.departure=ac.departure
            """
        query_inject_account_params = (
            self.id,
            filter_account_type_ids._ids,
            date_from,
            date_to,
            self.id,
            filter_account_type_ids._ids,
            self.date_since,
            date_from,
            self.id,
            self.env.uid
        )
        _logger.debug(query_inject_account % query_inject_account_params)
        self.env.cr.execute(query_inject_account, query_inject_account_params)
