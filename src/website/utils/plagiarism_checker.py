import base64
import time
from fileinput import filename
from django.utils import timezone
from datetime import datetime
import requests
import json
import os
from website.models import PlagiarismInfo
from copyleaks.copyleaks import Copyleaks
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.document import FileDocument
from copyleaks.models.submit.properties.pdf import Pdf
from copyleaks.models.export import ExportPdf, Export
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from dotenv import load_dotenv
load_dotenv()

# Register on https://api.copyleaks.com and grab your secret key (from the dashboard page).


class CopyleaksAPI:
    # Class-level variables to store token and expiration
    _auth_token = None
    _token_expiry = None

    def __init__(self, callback_host):
        """
        Initialize the Copyleaks API client and log in if necessary.
        """
        self.callback_host = callback_host
        self.login()

    @classmethod
    def login(cls):
        """
        Logs into the Copyleaks API and retrieves the authentication token.
        If a valid token already exists, it is reused.
        """
        email_address = os.environ.get('COPYLEAKS_ACCOUNT_EMAIL')
        api_key = os.environ.get('COPYLEAKS_API_KEY')
        if not email_address or not api_key:
            raise ValueError("Please provide an email address and API key")

        # Check if there's already a token and expiry
        if cls._auth_token and cls._token_expiry:
            # Ensure token expiry is timezone-aware
            if timezone.is_naive(cls._token_expiry):
                # Assuming 'Asia/Dhaka' as the timezone
                cls._token_expiry = timezone.make_aware(cls._token_expiry, timezone.get_current_timezone())

            # Compare with the current time (in the same timezone)
            current_time = timezone.now()
            if timezone.is_naive(current_time):
                current_time = timezone.make_aware(current_time, timezone.get_current_timezone())

            if current_time < cls._token_expiry:
                print("Using existing token.")
                return

        # Log in and get a new token if none exists or if it's expired
        try:
            token_data = Copyleaks.login(email_address, api_key)
            cls._auth_token = token_data
            expiry_time_str = token_data['.expires']
            print(f"Received expiry time: {expiry_time_str}")

            # Truncate microseconds to 6 digits before parsing
            expiry_time_str = expiry_time_str[:26] + 'Z'

            # Parse the expiration time and make it timezone-aware
            cls._token_expiry = datetime.strptime(expiry_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            cls._token_expiry = timezone.make_aware(cls._token_expiry, timezone.utc)  # Store as UTC

            print(f"Logged in successfully with token: {cls._auth_token}")
        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")
            exit(1)

    @staticmethod
    def encode_text_to_base64(text):
        """
        Convert text to a base64-encoded string.

        :param text: The plain text to convert.
        :return: base64-encoded content of the text.
        """
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    def submit_text(self, text, file_name, scan_id, sandbox=True):
        """
        Submit text for plagiarism checking without writing to a file.

        :param text: The plain text to submit for scanning.
        :param file_name: The name of the file for display in Copyleaks.
        :param scan_id: The ID of the scan.
        :param sandbox: Boolean to activate sandbox mode for testing.
        :return: Response from the API call.
        """
        # Ensure we are logged in and have a valid token
        self.login()

        # Encode the text directly to base64
        # file_base64 = self.encode_text_to_base64(text)

        # Create the file submission document
        file_submission = FileDocument(text, file_name)

        # Set the scan properties, including sandbox mode and webhook
        webhook_url = self.callback_host + 'plagiarism/webhook/?event={{STATUS}}'
        scan_properties = ScanProperties(webhook_url)
        scan_properties.set_sandbox(sandbox)
        scan_properties.set_expiration(24)
        pdf = Pdf()  # Creating instance of Pdf.
        pdf.set_create(True)  # Setting the create pdf to True to generate PDF report.
        pdf.set_title("Mediusware Ltd.")
        scan_properties.set_pdf(pdf)  # Will generate PDF report.

        file_submission.set_properties(scan_properties)

        # Submit the file to Copyleaks for scanning
        try:
            Copyleaks.submit_file(self._auth_token, scan_id, file_submission)
            print("File submitted for scanning. You will be notified via your webhook once the scan is completed.")
        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")

    def call_for_export(self, scan_id, export_id):
        # Ensure we are logged in and have a valid token
        self.login()
        # Set up the export process
        export = Export()
        export_completion_webhook_url = self.callback_host + 'plagiarism/webhook/export/'
        export.set_completion_webhook(export_completion_webhook_url)
        export.set_max_retries(3)
        export_pdf = ExportPdf()
        save_pdf_url = self.callback_host + f'export/{scan_id}/{export_id}/pdf-report/'
        export_pdf.set_endpoint(save_pdf_url)
        export_pdf.set_verb('POST')
        export.set_pdf_report(export_pdf)

        # Submit the export request
        try:
            Copyleaks.export(self._auth_token, scan_id, export_id, export)
            print("File submit for export. You will be notified via your webhook once the export is completed.")
        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")


def check_plagiarism(blogs, callback_host):
    plag_object = CopyleaksAPI(callback_host=callback_host)
    for blog in blogs:
        content = blog.collect_blog_content()  # Collect blog content
        plagiarism_info = PlagiarismInfo.objects.create(blog=blog)

        # print(f"Blog all section for the blog id: {blog.id}")

        filename = f"blog_{plagiarism_info.scan_id}_{plagiarism_info.export_id}.pdf"
        plag_object.submit_text(text=content, scan_id=plagiarism_info.scan_id, file_name=filename, sandbox=False)
        time.sleep(1)
