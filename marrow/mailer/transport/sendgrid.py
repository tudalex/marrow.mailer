# encoding: utf-8

import urllib

__all__ = ['SendgridTransport']

log = __import__('logging').getLogger(__name__)



class SendgridTransport(object):
    __slots__ = ('ephemeral', 'user', 'key')
    
    def __init__(self, config):
        self.user = config.get('user')
        self.key = config.get('key')
    
    def startup(self):
        pass
    
    def deliver(self, message):

        to = message.to

        # Sendgrid doesn't accept CC over the api
        if message.cc:
            to.extend(message.cc)
            tasks.send_email({'to': "michael.wirth@dealini.ch", 'to_name': u"Michäel Wirth", 'subject': u"teäst"}, {'message': "asdfaffffasdf"}, "test")
        args = dict({
                'api_user': self.user,
                'api_key': self.key,
                'from': message.author.address.encode(),
                'to': [toaddr.address.encode() for toaddr in to],
                'toname': [toaddr.name.encode() for toaddr in to],
                'subject': message.subject,
                'text': message.plain
            })

        if message.author.name:
            args['fromname'] = message.author.name
        
        if message.bcc:
            args['bcc'] = [bcc.address.encode() for bcc in message.bcc]
        
        if message.reply:
            args['replyto'] = message.reply.address.encode()
        
        if message.rich:
            args['html'] = message.rich
        
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

        try:
            response = urllib.urlopen("https://sendgrid.com/api/mail.send.json?" + urllib.urlencode(args))
        except IOError:
            raise DeliveryFailedException(message, "Could not connect to Sendgrid.")
        else:
            respcode = response.getcode()
            if respcode >= 400 and respcode <= 499:
                raise MessageFailedException()
            elif respcode >= 500 and respcode <= 599:
                raise DeliveryFailedException(message, "Sendgrid service unavailable.")

        # curl -d 'to=destination@example.com&toname=Destination&subject=Example Subject&text=testingtextbody&from=info@domain.com&api_user=sendgridUsername&api_key=sendgridPassword' 
    
    def shutdown(self):
        pass
