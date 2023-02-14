from odoo import models, fields, api


class TagModel(models.Model) :

    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.model", "sales_person", string="Properties", domain=[("state", "in", ["new", "offer_received"])]
    )