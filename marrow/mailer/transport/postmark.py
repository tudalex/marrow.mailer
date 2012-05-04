# encoding: utf-8

import urllib2
import json

from marrow.mailer.exc import MailConfigurationException, DeliveryFailedException, MessageFailedException

__all__ = ['PostmarkTransport']

log = __import__('logging').getLogger(__name__)


class PostmarkTransport(object):
    __slots__ = ('ephemeral', 'key', 'messages')
    
    def __init__(self, config):
        self.key = config.get('key')
        self.messages = []
    
    def _mapmessage(self, message):
        args = dict({
            'From': message.author.encode(message.encoding),
            'To': message.to.encode(message.encoding),
            'Subject': message.subject.encode(message.encoding),
            'TextBody': message.plain.encode(message.encoding),
        })
            
        if message.cc:
            args['Cc'] = message.cc.encode()

        if message.bcc:
            args['Bcc'] = message.bcc.encode(message.encoding)
        
        if message.reply:
            args['ReplyTo'] = message.reply.encode(message.encoding)
        
        if message.rich:
            args['HtmlBody'] = message.rich.encode(message.encoding)
        
        if message.attachments:
            # Not implemented yet
            """
            attachments = []
            
            for attachment in message.attachments:
                attachments.append((
                        attachment['Content-Disposition'].partition(';')[2],
                        attachment.get_payload(True)
                    ))
            
            msg.attachments = attachments
            """
            raise MailConfigurationException()

        return args

    def _batchsend(self):
        request = urllib2.Request(
                "https://api.postmarkapp.com/email/batch",
                json.dumps(self.messages),
                {
                    'Accept': "application/json",
                    'Content-Type': "application/json",
                    'X-Postmark-Server-Token': self.key,
                }
            )

        try:
            response = urllib2.urlopen(request)
        except (urllib2.HTTPError, urllib2.URLError), e:
            raise DeliveryFailedException(e, "Could not connect to Postmark.")
        else:
            respcode = response.getcode()
            if respcode >= 400 and respcode <= 499:
                raise MessageFailedException(response.read())
            elif respcode >= 500 and respcode <= 599:
                raise DeliveryFailedException(message, "Postmark service unavailable.")

        del self.messages[:]

    def startup(self):
        self.messages = []
    
    def deliver(self, message):
        if len(self.messages) >= 500:
            # Postmark allows to send a maximum of 500 emails over its batch API
            self._batchsend()
        
        args = self._mapmessage(message)
        self.messages.append(args)
    
    def shutdown(self):
        self._batchsend()