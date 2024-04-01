import os

import extract_msg
from typing import List, Optional

from langchain.document_loaders import Blob
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.parsers import PyMuPDFParser
from langchain.schema import Document


class MsgLoader(BaseLoader):
    """Load Outlook .msg file.

    Args:
        file_path: Path to the .msg file to load.
    """

    def __init__(self, file_path: str):
        """Initialize with file path."""
        self.file_path = file_path
        self.dir_name = os.path.dirname(self.file_path)

    def load(self) -> List[Document]:
        """Load from file path."""
        msg = extract_msg.Message(self.file_path)
        #os.chdir(self.dir_name)

        msg_sender = msg.sender
        msg_sender=(msg_sender if msg_sender else '')
        msg_message = (msg_sender if msg_sender else '') + '\n'+msg.body
        added_docs = []
        for attachment in msg.attachments:
            # Check if the attachment is a PDF
            if attachment.longFilename.lower().endswith('.pdf'):
                # Save the PDF
                save_path = os.path.join(self.dir_name, attachment.longFilename)
                # Save the PDF
                with open(save_path, 'wb') as f:
                    f.write(attachment.data)
                parser = PyMuPDFParser()
                blob = Blob.from_path(save_path)
                added_docs = parser.parse(blob)
        msg.close()

        metadata = {"source": self.file_path, "filename": msg.filename}
        return added_docs + [Document(page_content=msg_message, metadata=metadata)]

