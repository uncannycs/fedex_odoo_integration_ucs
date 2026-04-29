# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    fdx_tp_account_number = fields.Char(
        copy=False, string='FedEx Third-Party Billing Account', help="Enter the third-party account number for FedEx billing.")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fdx_tp_account_number = fields.Char(copy=False, string='FedEx Third-Party Billing Account',
                                                               help="Enter the third-party account number for FedEx billing.")
    fdx_tp_billing = fields.Boolean(string="FedEx Third-Party Billing", copy=False, default=False,
                                                          help="Enable this to allow third-party billing for FedEx shipments.")

    @api.onchange('partner_id', 'fdx_tp_account_number', 'fdx_tp_billing')
    def onchange_fdx_third_party(self):
        if self.fdx_tp_billing:
            if not self.fdx_tp_account_number and self.partner_id.fdx_tp_account_number:
                self.fdx_tp_account_number = self.partner_id.fdx_tp_account_number

            if self.fdx_tp_account_number != self.partner_id.fdx_tp_account_number:
                self.partner_id.fdx_tp_account_number = self.fdx_tp_account_number

        if not self.fdx_tp_billing:
            self.fdx_tp_account_number = ''
