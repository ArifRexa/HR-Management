import os
from io import BytesIO

from django.http import HttpResponse
from django.template.loader import get_template
from django.utils.crypto import get_random_string

from xhtml2pdf import pisa

import config.settings


class PDF:
    __FILE_PATH = config.settings.MEDIA_ROOT
    __FILE_EXTENSION = ".pdf"
    _letter_head = f"{config.settings.STATIC_ROOT}/stationary/letter_head_new.jpeg"
    _font = f"{config.settings.STATIC_ROOT}/stationary/bangla/Siyamrupali.ttf"

    def __init__(
        self,
        file_name=get_random_string(length=12),
        context=None,
        template_path=None,
        letter_head=None,
    ):
        if context is None:
            context = {}
        self.file_name = file_name
        self.context = context
        self.template_path = template_path

    def __get_string_from_template(self) -> BytesIO:
        """

        @return:
        """
        self.context["watermark"] = self._letter_head
        self.context["font"] = self._font
        template = get_template(self.template_path)
        html = template.render(self.context)
        result = BytesIO()
        pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        return result

    def render_to_pdf(self, download=config.settings.DOWNLOAD_PDF):
        """

        @param download:
        @return:
        """
        bytecode = self.__get_string_from_template()
        response = HttpResponse(bytecode.getvalue(), content_type="application/pdf")
        if download:
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{self.file_name}.pdf"'
        return response

    def create(self) -> str:
        """

        @return:
        """
        bytecode = self.__get_string_from_template()
        if config.settings.DEFAULT_S3_CLIENT:
            s3_client = config.settings.DEFAULT_S3_CLIENT
            file_obj = BytesIO(bytecode.getvalue())
            file_obj.seek(0)
            # Upload the file-like object to the Space
            try:
                s3_client.upload_fileobj(
                # s3_client.upload_file(
                    file_obj,
                    config.settings.AWS_STORAGE_BUCKET_NAME,
                    # self.absolute_file_path(),
                    f"media/{self.get_file_name()}",
                    ExtraArgs={'ContentType': 'application/pdf',
                               'ACL': 'public-read'}
                )
            except Exception as e:
                print('Upload error: ', e)
            file_url = f"{config.settings.MEDIA_URL}{self.get_file_name()}"
            print('at file upload: ', file_url, self.__FILE_EXTENSION)
            # print('at filename: ', bytecode.getvalue())
            return file_url

        else:
            print('absolute file path: ', self.absolute_file_path())
            file = open(self.absolute_file_path(), "wb")
            file.write(bytecode.getvalue())
            file.close()
            return self.absolute_file_path()

    def absolute_file_path(self):
        return f"{self.__FILE_PATH}/{self.file_name}{self.__FILE_EXTENSION}"

    def get_file_name(self):
        return self.file_name + self.__FILE_EXTENSION

    def delete(self) -> bool:
        """

        @param file_path:
        @return bool:
        """
        if os.path.exists(self.absolute_file_path()):
            os.remove(self.absolute_file_path())
            return True
        return False
