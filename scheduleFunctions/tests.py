from django.test import TestCase
from django.urls import reverse

login_name = "home"
dashboard_name = "dashboard"
run_script_name = "run_script"
class LoginViewTests(TestCase):
    def checkLoginExists(self):
        response = self.client.get(reverse(login_name))
        self.assertEqual(response.status_code, 200)
        
    def testLoginSuccess(self):
        form_data = {
            'username': 'testUser',
            'password': 'complexpassword',
            # ... other fields
        }
        response = self.client.post(reverse(login_name), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['username'], 'testUser')
        ...
        
    def testLoginFail(self):
        form_data = {
            'username': 'testUser',
            'password': 'badPassword',
            # ... other fields
        }
        response = self.client.post(reverse(login_name), form_data)
        self.assertEqual(response.status_code, 401)
        ...
        
class DashboardViewTests(TestCase):
    def testUserlessRedirect(self):
        response = self.client.get(reverse(dashboard_name))
        self.assertEqual(response.status_code, 302)
        
    def testDashboardSession(self):
        session = self.client.session
        session['username'] = 'testUser'
        session.save()
        
        response = self.client.get(reverse(dashboard_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['username'], 'testUser')
        ...
        
class ScriptViewTests(TestCase):
    def testScriptRun_converter(self):
        form_data = {
            'script': 'converter',
            # ... other fields
        }
        response = self.client.get(reverse(run_script_name), form_data)
        self.assertEqual(response.status_code, 200)
        ...
        
    def testScriptRun_identifier(self):
        form_data = {
            'script': 'identifier',
            # ... other fields
        }
        response = self.client.get(reverse(run_script_name), form_data)
        self.assertEqual(response.status_code, 200)
        ...