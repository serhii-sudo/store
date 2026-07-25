import unittest

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from subprocess import getoutput

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from user.models import CustomUser

options = Options()
options.binary_location = getoutput("find /snap/firefox -name firefox").split("\n")[-1]


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(
            service=Service(executable_path=getoutput("find /snap/firefox -name geckodriver").split("\n")[-1]),
            options=options,
        )

    def tearDown(self):
        self.driver.quit()

    def test_new_user_registration(self):
        self.driver.get(self.live_server_url)
        self.assertIn("Menu", self.driver.title)
        self.driver.find_element(By.LINK_TEXT, "Регистрация").click()
        self.assertIn("user-registration", self.driver.title)
        self.assertIn("registration", self.driver.current_url)

        # Получаем поля формы
        self.driver.find_element(By.ID, "id_username").send_keys("Bohdan")
        self.driver.find_element(By.ID, "id_email").send_keys("ostrovskii1991@gmail.com")
        self.driver.find_element(By.ID, "id_password1").send_keys("ostrog2022")
        self.driver.find_element(By.ID, "id_password2").send_keys("ostrog2022")

        # Находим кнопку нашей формы "Sign up"
        self.driver.find_element(By.CSS_SELECTOR, "button.btn").click()

        WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable((By.LINK_TEXT, "Выйти")))
        self.driver.find_element(By.LINK_TEXT, "Выйти").click()

        WebDriverWait(self.driver, 5).until(ec.url_contains("/"))
        self.assertNotIn("Выйти", self.driver.page_source)

        self.assertTrue(CustomUser.objects.filter(username="Bohdan").exists())
        new_user = CustomUser.objects.get(email="ostrovskii1991@gmail.com")
        print(new_user.email)


if __name__ == "__main__":
    unittest.main()
