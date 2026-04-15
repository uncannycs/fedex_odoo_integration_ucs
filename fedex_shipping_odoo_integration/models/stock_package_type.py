# -*- coding:utf-8 -*-
from odoo import fields, models, api


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(selection=[('fedex_shipping_provider', 'Fedex')])
