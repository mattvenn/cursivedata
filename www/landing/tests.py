
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class LandingPageTest(TestCase):

    def test_landing_logged_out(self):
        landing_page_url = reverse('landing')
        response = self.client.get(landing_page_url)
        login_page_url = reverse('login') + '?next=' + landing_page_url
        self.assertRedirects(response, login_page_url)

    def test_landing_logged_in(self):
        user = User.objects.create_user(username='admin', password='secret')
        self.client.login(username='admin', password='secret')
        landing_page_url = reverse('landing')
        response = self.client.get(landing_page_url)
        self.assertRedirects(response, reverse('cursivedata:index'))
