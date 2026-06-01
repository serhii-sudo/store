from http import HTTPStatus

from django.test import TestCase


class TestUserPageCase(TestCase):

    def test_template_content_user_registration(self):
        response = self.client.get("/user/registration/")

        self.assertContains(response, "<title>user-registration</title>", html=True)
        self.assertTemplateUsed(response, "user/registration.html")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_template_content_user_authorization(self):
        response = self.client.get("/user/authorization/")

        self.assertContains(response, "<title>user-authorization</title>", html=True)
        self.assertTemplateUsed(response, "user/authorization.html")
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestUserFormFields(TestCase):
    def test_form_registration_fields(self):
        response = self.client.get("/user/registration/")

        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_form_authorization_fields(self):
        response = self.client.get("/user/authorization/")

        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_form_ids_registration(self):
        response = self.client.get("/user/registration/")

        self.assertContains(response, 'id="id_username"')
        self.assertContains(response, 'id="id_email"')
        self.assertContains(response, 'id="id_password1"')
        self.assertContains(response, 'id="id_password2"')

    def test_form_ids_authorization(self):
        response = self.client.get("/user/authorization/")

        self.assertContains(response, 'id="id_username"')
        self.assertContains(response, 'id="id_password"')

    def test_form_buttons_registration(self):
        response = self.client.get("/user/registration/")

        # testing the Submit  button
        self.assertContains(response, "Sign up")
        self.assertContains(response, 'type="submit"')
        self.assertEqual(response.status_code, 200)

        # testing the Google button
        self.assertContains(response, "Sign up with Google")
        self.assertContains(response, "google-oauth2")
        self.assertEqual(response.status_code, 200)

        # testing the Telegram button
        self.assertContains(response, "Sign up with Telegram")
        self.assertContains(response, 'href="/user/telegram/start/"')
        self.assertEqual(response.status_code, 200)

    def test_form_buttons_authorization(self):
        response = self.client.get("/user/authorization/")

        self.assertContains(response, "Log in")
        self.assertContains(response, 'type="submit"')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Log in with Google")
        self.assertContains(response, "google-oauth2")
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Log in with Telegram")
        self.assertContains(response, 'href="/user/telegram/start/"')
        self.assertEqual(response.status_code, 200)
