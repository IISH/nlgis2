import unittest

import demo


class DemoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = demo.app.test_client()

    # NLGIS-14, SIKS-33
    def test_provinces_dropdown(self):
        provinces = (
            "Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Gelderland", "Utrecht", "Noord-Holland",
            "Zuid-Holland", "Zeeland", "Noord-Brabant", "Limburg")

        # A selected province should not be in the dropdown list.
        for province in provinces:
            url = '/site?custom=on&code=NLSTR&province=' + province
            option = '<option value="' + province + '">' + province + '</option>'
            rv = self.app.get(url)
            assert option not in rv.data, province + " should not be in the dropdown"

        # All provinces should be in the drop down list if none were selected.
        url = '/site?custom=on&code=NLSTR'
        rv = self.app.get(url)
        missing_options = []
        for province in provinces:
            option = '<option value="' + province + '">' + province + '</option>'
            if not option in rv.data:
                missing_options.append(province)
        assert not missing_options, ",".join(missing_options) + " should be in the dropdown but they are not."


if __name__ == '__main__':
    unittest.main()