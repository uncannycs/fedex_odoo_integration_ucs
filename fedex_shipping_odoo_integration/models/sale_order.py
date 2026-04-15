# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    fedex_third_party_account_number_sale_order = fields.Char(
        copy=False, string='FexEx Third-Party Account Number', help="Please Enter the Third Party account number ")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fedex_third_party_account_number_sale_order = fields.Char(copy=False, string='FexEx Third-Party Account Number',
                                                              help="Please Enter the Third Party account number ")
    fedex_bill_by_third_party_sale_order = fields.Boolean(string="FedEx Third Party Payment", copy=False, default=False,
                                                          help="when this fields is true,then we can visible fedex_third party account number")

    @api.onchange('partner_id', 'fedex_third_party_account_number_sale_order', 'fedex_bill_by_third_party_sale_order')
    def onchange_fedex_third_party(self):
        if self.fedex_bill_by_third_party_sale_order:
            if not self.fedex_third_party_account_number_sale_order and self.partner_id.fedex_third_party_account_number_sale_order:
                self.fedex_third_party_account_number_sale_order = self.partner_id.fedex_third_party_account_number_sale_order

            if self.fedex_third_party_account_number_sale_order != self.partner_id.fedex_third_party_account_number_sale_order:
                self.partner_id.fedex_third_party_account_number_sale_order = self.fedex_third_party_account_number_sale_order

        if not self.fedex_bill_by_third_party_sale_order:
            self.fedex_third_party_account_number_sale_order = ''
