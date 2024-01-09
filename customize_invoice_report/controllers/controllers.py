# -*- coding: utf-8 -*-
# from odoo import http


# class CustomizeInvoiceReport(http.Controller):
#     @http.route('/customize_invoice_report/customize_invoice_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customize_invoice_report/customize_invoice_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('customize_invoice_report.listing', {
#             'root': '/customize_invoice_report/customize_invoice_report',
#             'objects': http.request.env['customize_invoice_report.customize_invoice_report'].search([]),
#         })

#     @http.route('/customize_invoice_report/customize_invoice_report/objects/<model("customize_invoice_report.customize_invoice_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customize_invoice_report.object', {
#             'object': obj
#         })
