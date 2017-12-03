from django.core.mail import send_mail, BadHeaderError
from django.forms import ChoiceField, Form, CharField, EmailField, PasswordInput
from django.http import HttpResponse, HttpResponseRedirect
from .models import Channels
from django.conf import settings


class TeamChannelsForm(Form):
    def __init__(self, team, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        self.request = kwargs.pop('request', None)
        super(TeamChannelsForm, self).__init__(*args, **kwargs)
        self.fields['channels'] = ChoiceField(
            choices=[(ch.chanel_name, str(ch.chanel_name)) for ch in Channels.objects.filter(team=team)])


class SendMessage(Form):
    your_email = EmailField()
    your_password = CharField(widget=PasswordInput)
    to_email = EmailField()

    def send_email(self):
        cd = self.cleaned_data
        settings.EMAIL_HOST_PASSWORD = cd['your_password']
        settings.EMAIL_HOST_USER = cd['your_email']
        client_id = settings.CLIENT_ID
        post_url = "https://slack.com/oauth/authorize?scope=bot&client_id="+client_id
        subject = '({}) invite you moderation'.format(cd['your_email'])
        message = 'Authorization in slack {}'.format(post_url)
        send_mail(subject, message, cd['your_email'], [cd['to_email']])
