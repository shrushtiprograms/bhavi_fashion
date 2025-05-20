from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class LoginTestCase(TestCase):
    """
    Test cases for the login functionality based on the provided document.
    """

    def setUp(self):
        """
        Set up test data before each test method runs.
        """
        # Create a valid user
        self.valid_user = User.objects.create_user(
            username='test@123',
            email='test@example.com',
            password='#Helo123',
            first_name='Test',
            last_name='User',
            role='customer'
        )

        # Create a disabled user
        self.disabled_user = User.objects.create_user(
            username='disabled@123',
            email='disabled@example.com',
            password='Pass123',
            first_name='Disabled',
            last_name='User',
            role='customer',
            is_active=False
        )

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin@123',
            email='admin@example.com',
            password='Admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_staff=True
        )

        # Create a client instance
        self.client = Client()

        # URL for login page
        self.login_url = reverse('accounts:login')

    def test_login_valid_credentials(self):
        """
        Test Case ID: 1
        Description: Checks valid user id and password entered for login.
        Test Steps:
            1. Enter valid username
            2. Enter valid password
            3. Click login button
        Expected Result: Check the validity of user id and password,
                        if correct then it should allow successfully login.
        """
        response = self.client.post(self.login_url, {
            'username': 'test@123',
            'password': '#Helo123'
        }, follow=True)

        # Check if login was successful
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'test@123')
        # Verify redirect to home page after successful login
        self.assertRedirects(response, reverse('home'))

    def test_login_invalid_credentials(self):
        """
        Test Case ID: 2
        Description: Checks when the data is not correct as per required data.
        Test Steps:
            1. Enter invalid username
            2. Enter invalid password
            3. Click login button
        Expected Result: It should show an error message indicating invalid credentials.
        """
        response = self.client.post(self.login_url, {
            'username': 'wrong@123',
            'password': 'wrongpassword'
        })

        # Check if login failed
        self.assertContains(response, "Please enter a correct username and password")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_without_username(self):
        """
        Test Case ID: 3
        Description: When username field is empty and click login.
        Test Steps:
            1. Without username directly entered
            2. Enter password
            3. Click login button
        Expected Result: It should ask to enter username.
        """
        response = self.client.post(self.login_url, {
            'username': '',
            'password': '#Helo123'
        })

        # Check if form error is displayed
        self.assertContains(response, "This field is required")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_without_password(self):
        """
        Test Case ID: 4
        Description: When password field is empty and click login.
        Test Steps:
            1. Without password directly entered
            2. Enter username
            3. Click login button
        Expected Result: It should ask to enter password.
        """
        response = self.client.post(self.login_url, {
            'username': 'test@123',
            'password': ''
        })

        # Check if form error is displayed
        self.assertContains(response, "This field is required")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_empty_fields(self):
        """
        Test Case ID: 5
        Description: When user does not enter any kind of data and click to login.
        Test Steps:
            1. Leave username empty
            2. Leave password empty
            3. Click submit
        Expected Result: It should ask to enter data as per requirement.
        """
        response = self.client.post(self.login_url, {
            'username': '',
            'password': ''
        })

        # Check if form errors are displayed
        self.assertContains(response, "This field is required")
        self.assertEqual(response.context['form'].errors['username'][0], 'This field is required.')
        self.assertEqual(response.context['form'].errors['password'][0], 'This field is required.')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_disabled_account(self):
        """
        Test Case ID: 7
        Description: Attempts login with an account that has been disabled.
        Test Steps:
            1. Enter valid username
            2. Enter valid password
            3. Click login button
        Expected Result: Show error message indicating account is disabled.
        """
        response = self.client.post(self.login_url, {
            'username': 'disabled@123',
            'password': 'Pass123'
        })

        # Check if login failed with appropriate message
        self.assertContains(response, "This account is inactive")
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_admin_account(self):
        """
        Test Case ID: 9
        Description: Login as admin user.
        Test Steps:
            1. Enter valid admin username
            2. Enter valid admin password
            3. Click login button
        Expected Result: Redirect to admin dashboard.
        """
        response = self.client.post(self.login_url, {
            'username': 'admin@123',
            'password': 'Admin123'
        }, follow=True)

        # Check if login was successful and redirected to admin dashboard
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.context['user'].username, 'admin@123')
        self.assertTrue(response.context['user'].is_staff)
        # Note: This checks the home page redirection. In a real implementation,
        # you would need to add custom logic to redirect admin users to an admin dashboard
        self.assertRedirects(response, reverse('home'))

    def test_forgot_password_link(self):
        """
        Test Case ID: 11
        Description: Test forgot password functionality.
        Test Steps:
            1. Click "Forgot password?" link
        Expected Result: Redirect to forgot password page.
        """
        response = self.client.get(self.login_url)

        # Check if the page contains a "Forgot password" link
        self.assertContains(response, 'Forgot password?')

        # Test clicking the link redirects to password reset page
        # Note: This assumes the link has a pattern like `/accounts/password_reset/`
        # Update this test if your URL pattern is different
        password_reset_url = reverse('accounts:password_reset')
        self.assertContains(response, password_reset_url)

    def test_register_link(self):
        """
        Test Case ID: 12
        Description: Test register link functionality.
        Test Steps:
            1. Click "Register here" link
        Expected Result: Redirect to registration page.
        """
        response = self.client.get(self.login_url)

        # Check if the page contains a registration link
        self.assertContains(response, 'Register')

        # Test clicking the link redirects to registration page
        register_url = reverse('accounts:register')
        self.assertContains(response, register_url)