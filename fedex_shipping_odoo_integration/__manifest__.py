# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2024 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    "name": "FedEx Shipping Odoo Integration",
    "category": "Website",
    "version": "17.0.1.0.0",
    "summary": """ """,
    "description": """ Our Odoo FedEx Shipping Integration will help you connect with FedEx Shipping Carrier with Odoo. automatically submit order information from Odoo to FedEx and get Shipping label, and Order Tracking number from FedEx to Odoo.we also provide the ups,dhl,usps,stamp.com,shipstation shipping integration.""",
    "depends": ["base","delivery","stock_delivery","purchase"],
    "data": [
            "data/ir_cron.xml",
            "data/delivery_fedex.xml",
            "views/res_company.xml",
            "views/delivery_carrier_view.xml",
            "views/sale_view.xml",
            ],
    "author": "Uncanny Consulting Services LLP",
    "website": "https://www.vrajatechnologies.com",
    "maintainer": "Uncanny Consulting Services LLP",
    "live_test_url": "https://www.vrajatechnologies.com/contactus",
    "images": ["static/description/cover.jpg"],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "price": "99",
    "currency": "EUR",
    "license": "OPL-1",

}
