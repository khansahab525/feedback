# -*- coding: utf-8 -*-
# from odoo import http


# class FeedEmployee(http.Controller):
#     @http.route('/feed_employee/feed_employee', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/feed_employee/feed_employee/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('feed_employee.listing', {
#             'root': '/feed_employee/feed_employee',
#             'objects': http.request.env['feed_employee.feed_employee'].search([]),
#         })

#     @http.route('/feed_employee/feed_employee/objects/<model("feed_employee.feed_employee"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('feed_employee.object', {
#             'object': obj
#         })
