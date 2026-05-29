from http import HTTPStatus


from django.test import TestCase


class TestHomePageCase(TestCase):
    def test_template_content_home(self):
        response = self.client.get("/")

        self.assertTemplateUsed(response, "products/home.html")
        self.assertContains(response, "<title>Menu</title>", html=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
