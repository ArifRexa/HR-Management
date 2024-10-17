import base64
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
    def __init__(self, callback_host):
        """
        Initialize the Copyleaks API client.

        :param email_address: The email associated with your Copyleaks account.
        :param api_key: The secret key from the Copyleaks dashboard.
        """
        self.callback_host = callback_host
        email_address = os.environ.get('COPYLEAKS_ACCOUNT_EMAIL')
        api_key = os.environ.get('COPYLEAKS_API_KEY')
        if not email_address or not api_key:
            print(f"please provide an email address and API key")
            raise ValueError("please provide an email address and API key")
        try:
            self.auth_token = Copyleaks.login(email_address, api_key)
            print(f"Logged in successfully with token: {self.auth_token}")
        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")
            exit(1)

    def encode_text_to_base64(self, text):
        """
        Convert text to a base64-encoded string.

        :param text: The plain text to convert.
        :return: base64-encoded content of the text.
        """
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        return encoded_text

    def submit_text(self, text, file_name, scan_id, export_id, sandbox=True):
        """
        Submit text for plagiarism checking without writing to a file.

        :param text: The plain text to submit for scanning.
        :param file_name: The name of the file for display in Copyleaks.
        :param scan_id: The ID of the scan.
        :param export_id: The ID of the export.
        :param sandbox: Boolean to activate sandbox mode for testing.
        :return: Response from the API call.
        """
        # Encode the text directly to base64
        file_base64 = self.encode_text_to_base64(text)

        # Create the file submission document
        file_submission = FileDocument(file_base64, file_name)

        # Set the scan properties, including sandbox mode and webhook
        webhook_url = self.callback_host + 'plagiarism/webhook/?event={{STATUS}}'
        scan_properties = ScanProperties(webhook_url)
        scan_properties.set_sandbox(sandbox)
        scan_properties.set_expiration(24)
        pdf = Pdf() # Creating instance of Pdf.
        pdf.set_create(True) # Setting the create pdf to True to generate PDF report.
        scan_properties.set_pdf(pdf) # Will generate PDF report.

        file_submission.set_properties(scan_properties)


        # Submit the file to Copyleaks for scanning
        try:
            Copyleaks.submit_file(self.auth_token, scan_id, file_submission)
            print("File submitted for scanning. You will be notified via your webhook once the scan is completed.")

        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")

        export = Export()
        export_completion_webhook_url = self.callback_host + 'plagiarism/webhook/export'
        export.set_completion_webhook(export_completion_webhook_url)
        export_pdf = ExportPdf()
        save_pdf_url = self.callback_host + f'/export/{scan_id}/{export_id}/pdf-report/'
        export_pdf.set_endpoint(save_pdf_url)
        export_pdf.set_verb('POST')
        export_pdf.set_headers([['key', 'value'], ['key2', 'value2']])  # optional
        export.set_crawled_version(export_pdf)


        try:
            Copyleaks.export(self.auth_token, scan_id, export_id, export)
            print("File submit for export. You will be notified via your webhook once the scan is completed.")

        except CommandError as ce:
            response = ce.get_response()
            print(f"Error {response.status_code}: {response.content}")


def check_plagiarism(blog):
    content = blog.collect_blog_content()  # Collect blog content
    plagiarism_info = PlagiarismInfo.objects.create(blog=blog)

    print(f"{'-'*100}")
    print(plagiarism_info.scan_id, plagiarism_info.export_id)
    print(f"Blog all section for the blog id: {blog.id}")
    print(content)
    generate_scan_id = blog.id
    return content
