# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from odoo import api, models


class IrAccess(models.Model):
    """Add authenticated_partner_id in access domain evaluation context.

    This come from the env current odoo environment which is
    populated by dependency method authenticated_partner_env or authenticated_partner
    when a route handler depends one of them and is called by the FastAPI service layer.

    Odoo 20 replaced `ir.rule` by `ir.access`: `_eval_context` is the same hook, and
    `_get_access_context` names the context values the evaluated domain depends on (the keys
    that `ir.rule._compute_domain_keys` returned before).
    """

    _inherit = "ir.access"

    @api.model
    def _eval_context(self):
        ctx = super()._eval_context()
        ctx["authenticated_partner_id"] = self.env.context.get(
            "authenticated_partner_id", False
        )
        return ctx

    def _get_access_context(self):
        yield from super()._get_access_context()
        yield self.env.context.get("authenticated_partner_id", False)
