import logging
from gmail import Message, GMailWorker, GMail  # https://github.com/paulc/gmail-sender
from markdown import Markdown, markdown
from io import StringIO
import os


class StrippedMarkdown:
    def unmarkElement(self, element, stream=None):
        if stream is None:
            stream = StringIO()
        if element.text:
            stream.write(element.text)
        for sub in element:
            self.unmarkElement(sub, stream)
        if element.tail:
            stream.write(element.tail)
        return stream.getvalue()

    # patching Markdown
    Markdown.output_formats["plain"] = unmarkElement
    __md = Markdown(output_format="plain")
    __md.stripTopLevelTags = False

    def unmark(self, text):
        return self.__md.convert(text)


class Gmail:
    def __init__(self, appName: str,
                 sender: str = os.environ['GMAIL_USERID'],
                 gmailToken: str = os.environ['GMAIL_TOKEN'],
                 debug=False):
        self.gmail = None
        self.appName = appName
        if debug:
            logging.info(f'Gmail server enabled in DEBUG MODE.')
            self.gmail = GMail(f'{appName} <{sender}>', gmailToken)
        else:
            logging.info(f'Gmail server enabled.')
            self.gmail = GMailWorker(f'{appName} <{sender}>', gmailToken)

    # TODO: merge message/htmlMessageBody to be markup
    def sendEmail(self, sendTo: str, emailSubject: str = '', messageBody: str = ''):
        # if there is noone to send it to or no gmail token return
        if not sendTo or not self.gmail:
            return

        messageBody = messageBody + f'\n\n---\n###### ***Email sent by {self.appName}***\n'
        htmlMessageBody = markdown(messageBody)

        logging.info(f"sending email titled '{emailSubject}'")
        msg = Message(
            subject=emailSubject,
            to=sendTo,
            text=messageBody,
            html=htmlMessageBody,
            reply_to='do@notreply.com',
        )
        self.gmail.send(msg)
        logging.info(f'Email sent to {sendTo}.')
