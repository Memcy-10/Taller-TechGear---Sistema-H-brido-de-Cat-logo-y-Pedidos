from django.test import SimpleTestCase


class OrdenesViewTests(SimpleTestCase):
    def test_listado_de_ordenes_disponible_en_la_web(self):
        response = self.client.get('/ordenes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ordenes')
