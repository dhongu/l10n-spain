## 20.0.1.0.1 (2026-11-16)

**Changed**

- Apps Store page (`static/description/index.html`) regenerated with the Terrabit template.

## 20.0.1.0.0 (2026-11-16)

**Changed**

- Migration to Odoo 20: the PostgreSQL codes to retry are defined in the module
  (`odoo.service.model.PG_CONCURRENCY_ERRORS_TO_RETRY` was removed) and the relink
  position uses `ir.config_parameter` `get_int` / `set_int`.

## 19.0.1.0.0 (2026-11-16)

**Added**

- Spanish localities with postal code and region, from GeoNames.
- City and region filled in from the postal code on Spanish addresses; action and scheduled action to
  link the existing contacts.
- Consultant sheet (readme/FISA_CONSULTANT.md) and screenshots, in English.
