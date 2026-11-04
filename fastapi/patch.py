# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from urllib.parse import parse_qs, urlparse

from odoo.http import router
from odoo.http.router import db_filter

# Odoo 20 has no `Request._get_session_and_dbname`: the database of a request is chosen by the
# function `odoo.http.router._set_session_and_dbname(request)`, which the router and the retrying
# loop call by name. The patch runs after it and fills in the database from the "db" parameter
# when the standard rules found none.
_original_set_session_and_dbname = router._set_session_and_dbname


def _patched_set_session_and_dbname(request):
    _original_set_session_and_dbname(request)
    if not request.db:
        # Try to get the database from request "db" param.
        # This is useful for multi-database environments.
        db = request.httprequest.args.get("db", "").strip()
        if not db:
            # For browser sub-requests (e.g. openapi.json or static assets fetched
            # by Swagger UI / ReDoc), the browser sets a Referer header pointing
            # to the docs page which may carry the "db" query parameter.
            referer = request.httprequest.headers.get("Referer", "")
            if referer:
                parsed = urlparse(referer)
                db = parse_qs(parsed.query).get("db", [""])[0].strip()
        if db and db_filter([db]):
            request.db = db
            request.session.db = db


router._set_session_and_dbname = _patched_set_session_and_dbname
