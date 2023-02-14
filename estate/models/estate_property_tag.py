from odoo import models, fields, api


class TagModel(models.Model) :
    _name = "tag.model"
    _description = "Tag Model"
    _order = "name desc"


    name = fields.Char(string="Name", required=True)
    color = fields.Integer("Color Index")
    _sql_constraints = [
        ("check_name", "unique(name)", "The tag name must be unique"),
    ]
