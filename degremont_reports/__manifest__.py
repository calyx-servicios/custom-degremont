# -*- coding: utf-8 -*-
{
    'name': "Degremont Reports",
    'summary': """ """,
    'description': """ """,
    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",
    'category': 'Tools',
    'version': '11.0.1.0.1',
    'depends': ['account','account_payment_group','account_payment_group_document','account_extension','manual_currency_exchange_rate','account_withholding_automatic_extension'],
    'data': [
        "wizard/analytic_line_report_wizard_view.xml",
        "report/report_analytic_lines_view.xml",
        "report/payment_view.xml",
        'report/purchase_report.xml',
        'report/templates/layouts.xml',
        'report/templates/report_analytic_lines.xml',
        'report/reports.xml',
        'menuitems.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
    ],
}
