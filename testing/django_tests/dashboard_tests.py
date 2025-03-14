from django.test import TestCase
from django.urls import reverse

view_name = "dashboard"

class DashboardViewTests(TestCase):
    def testUserlessRedirect(self):
        response = self.client.get(reverse(view_name))
        self.assertEqual(response.status_code, 302)
        
    def testDashboardSession(self):
        session = self.client.session
        session['username'] = 'testUser'
        session.save()
        
        response = self.client.get(reverse(view_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['username'], 'testUser')
        ...
        
    def testScriptRun_converter(self):
        form_data = {
            'script': 'converter',
            # ... other fields
        }
        response = self.client.get(reverse("run_script"), form_data)
        self.assertEqual(response.status_code, 200)
        ...
        
    def testScriptRun_identifier(self):
        form_data = {
            'script': 'identifier',
            # ... other fields
        }
        response = self.client.get(reverse("run_script"), form_data)
        self.assertEqual(response.status_code, 200)
        ...