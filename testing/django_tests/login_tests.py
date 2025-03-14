from django.test import TestCase
from django.urls import reverse

view_name = "home"
class LoginViewTests(TestCase):
    def checkLoginExists(self):
        response = self.client.get(reverse(view_name))
        self.assertEqual(response.status_code, 200)
        
    def testLoginSuccess(self):
        form_data = {
            'username': 'testUser',
            'password': 'complexpassword',
            # ... other fields
        }
        response = self.client.post(reverse(view_name), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['username'], 'testUser')
        ...
        
    def testLoginFail(self):
        form_data = {
            'username': 'testUser',
            'password': 'badPassword',
            # ... other fields
        }
        response = self.client.post(reverse(view_name), form_data)
        self.assertEqual(response.status_code, 401)
        ...