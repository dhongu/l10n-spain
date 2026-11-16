# ©  2026 Terrabit
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from unittest.mock import patch

from odoo.tests import Form, TransactionCase, tagged

from odoo.addons.l10n_es_zip import hooks
from odoo.addons.l10n_es_zip.models.res_partner import RELINK_PARAM


@tagged("post_install", "-at_install")
class TestCityFromZip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country = cls.env.ref("base.es")
        cls.Partner = cls.env["res.partner"]

    def _city(self, zip_code, name):
        return self.env["res.city"].search(
            [("country_id", "=", self.country.id), ("zipcode", "=", zip_code), ("name", "=", name)]
        )

    def test_data_loaded(self):
        self.assertTrue(self.country.enforce_cities)
        city = self._city("01160", "Ibarra")
        self.assertEqual(len(city), 1)
        self.assertEqual(city.state_id, self.env.ref("base.state_es_vi"))

    def test_unique_zip(self):
        city, state = self.Partner._l10n_es_city_from_zip("01160")
        self.assertEqual(city, self._city("01160", "Ibarra"))
        self.assertEqual(state, self.env.ref("base.state_es_vi"))

    def test_shared_zip_gives_state(self):
        # 01007 is shared by several localities of the same region: only the region is known
        city, state = self.Partner._l10n_es_city_from_zip("01007")
        self.assertFalse(city)
        self.assertEqual(state, self.env.ref("base.state_es_vi"))
        # the city name picks the locality
        city, state = self.Partner._l10n_es_city_from_zip("01007", "Armentia".upper())
        self.assertEqual(city, self._city("01007", "Armentia"))

    def test_onchange_zip(self):
        # not saved: other modules may make more fields required on the contact form
        partner_form = Form(self.Partner)
        partner_form.name = "Test Partner"
        partner_form.country_id = self.country
        partner_form.zip = "01160"
        self.assertEqual(partner_form.city_id, self._city("01160", "Ibarra"))
        self.assertEqual(partner_form.city, "Ibarra")
        self.assertEqual(partner_form.state_id, self.env.ref("base.state_es_vi"))

    def test_fix_city_from_zip(self):
        partner = self.Partner.create(
            {"name": "Test Partner", "country_id": self.country.id, "city": "Ibarra", "zip": "01160"}
        )
        partner.l10n_es_fix_city_from_zip()
        self.assertRecordValues(
            partner,
            [
                {
                    "city_id": self._city("01160", "Ibarra").id,
                    "city": "Ibarra",
                    "zip": "01160",
                    "state_id": self.env.ref("base.state_es_vi").id,
                }
            ],
        )

    def test_other_country_untouched(self):
        partner = self.Partner.create(
            {"name": "Ion Popescu", "country_id": self.env.ref("base.ro").id, "city": "Ibarra", "zip": "01160"}
        )
        partner.l10n_es_fix_city_from_zip()
        self.assertFalse(partner.city_id)
        self.assertFalse(partner.state_id)

    def test_relink_batch(self):
        partner = self.Partner.create(
            {"name": "Test Partner", "country_id": self.country.id, "city": "Ibarra", "zip": "01160"}
        )
        last_id, count = self.Partner._l10n_es_relink_batch(partner.id - 1)
        self.assertGreaterEqual(count, 1)

    def _create_partner(self, name="Test Partner"):
        return self.Partner.create({"name": name, "country_id": self.country.id, "city": "Ibarra", "zip": "01160"})

    def test_relink_batch_limit(self):
        first = self._create_partner("Test Partner 1")
        second = self._create_partner("Test Partner 2")
        last_id, count = self.Partner._l10n_es_relink_batch(first.id - 1, limit=1)
        self.assertEqual((last_id, count), (first.id, 1))
        self.assertTrue(first.city_id)
        self.assertFalse(second.city_id)

    def test_cron_resumes_and_finishes(self):
        params = self.env["ir.config_parameter"].sudo()
        partner = self._create_partner()
        cron_model = type(self.env["ir.cron"])
        # saved position before the contact: the cron resumes from it, relinks it and finishes
        params.set_int(RELINK_PARAM, partner.id - 1)
        with patch.object(cron_model, "_commit_progress", return_value=float("inf")) as progress:
            self.Partner._cron_l10n_es_relink_partners()
        self.assertTrue(partner.city_id)
        self.assertEqual(params.get_int(RELINK_PARAM), 0)
        progress.assert_called_with(remaining=0, deactivate=True)

    def test_post_init_hook_large_database_uses_cron(self):
        self._create_partner()
        cron = self.env.ref("l10n_es_zip.ir_cron_relink_partners")
        cron.active = False
        with patch.object(hooks, "RELINK_BATCH", 0):
            hooks.post_init_hook(self.env)
        self.assertTrue(cron.active)
