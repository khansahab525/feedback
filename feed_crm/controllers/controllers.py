# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class ShopifyWebhookController(http.Controller):

    @http.route('/shopify/webhook/orders/create', type='json', auth='none')
    def shopify_order_create(self):
        return 'hello'
        # Parse the incoming JSON data automatically handled by Odoo
        # data = request.jsonrequest
        #
        # # Process the data
        # # Add your logic here
        #
        # return json.dumps({'success': True})

