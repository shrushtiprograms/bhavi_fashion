#!/usr/bin/env python
"""
This script runs the login test cases and generates a detailed report.
"""
import os
import sys
import django
import unittest
from datetime import datetime

# Setup Django environment
# Go two levels up: from tests/login → tests → bhavi_fashion (outer)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bhavi_fashion.settings')
django.setup()

from tests.login.test_login import LoginTestCase

if __name__ == '__main__':
    # Create a test suite with our test case
    suite = unittest.TestLoader().loadTestsFromTestCase(LoginTestCase)

    # Get current date and time for report file name
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"login_test_report_{now}.txt"

    print(f"Running login component test cases...")
    print(f"Results will be saved to {report_file}")

    # Run the tests and capture the output
    with open(report_file, 'w') as f:
        f.write("BHAVI INDIA FASHION - LOGIN COMPONENT TEST REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Date and Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        # Run the tests with a custom test runner that writes to our file
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        result = runner.run(suite)

        # Write summary
        f.write("\n" + "=" * 60 + "\n")
        f.write("TEST SUMMARY\n")
        f.write(f"Total Tests: {result.testsRun}\n")
        f.write(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}\n")
        f.write(f"Failed: {len(result.failures)}\n")
        f.write(f"Errors: {len(result.errors)}\n")

        # Print result to console
        print(f"\nTEST SUMMARY:")
        print(f"Total Tests: {result.testsRun}")
        print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Failed: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"\nDetailed report saved to {report_file}")