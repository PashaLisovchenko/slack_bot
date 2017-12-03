from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin, FormView
from slackclient import SlackClient

from bot.forms import TeamChannelsForm, SendMessage
from bot.models import Team, LeaveMessage, AnswerMessage, Channels
import requests
import json


def slack_oauth_view(request):
    code = request.GET['code']

    params = {
        'code': code,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
    }
    url = 'https://slack.com/api/oauth.access'
    json_response = requests.get(url, params)
    data = json.loads(json_response.text)
    slack_client = SlackClient(settings.BOT_TOKEN)
    private_channels = slack_client.api_call(
        'groups.list'
    )
    public_channels = slack_client.api_call(
        'channels.list'
    )
    all_channels = [chanel['name'] for chanel in private_channels['groups']] + \
                   [chanel['name'] for chanel in public_channels['channels']]
    team, created = Team.objects.get_or_create(
        team_name=data['team_name'],
        team_id=data['team_id']
    )
    password = data['user_id']*2
    if not request.user.is_authenticated:
        slack_client = SlackClient(settings.BOT_TOKEN)
        profile = slack_client.api_call('users.profile.get')['profile']
        user = authenticate(
            request=request,
            username=data['user_id'],
            password=password
        )
        if user is None:
            user = User.objects.create_user(
                username=data['user_id'],
                email=profile['email']
            )
            user.set_password(password)
            if created:
                user.is_staff = True
            user.save()
            team.users.add(user)
        login(
            request=request,
            user=user
        )
    else:
        user = request.user
    if created:
        team.admin = user
        team.save()
    for ch in all_channels:
        Channels.objects.get_or_create(
            team=team,
            chanel_name=ch
        )
    return redirect('slack:list_team')


@csrf_exempt
@require_POST
def take_ask_message_view(request):
    if request.POST.get('token') == settings.VERIFICATION_TOKEN:
        data = request.POST
        team = Team.objects.get(team_id=data.get('team_id'))
        channels = Channels.objects.filter(team=team)
        active_chanel = [ch for ch in channels if ch.active_chanel]
        if active_chanel:
            chanel = active_chanel[0].chanel_name
        else:
            chanel = 'general'
        slack_client = SlackClient(settings.BOT_TOKEN)
        ask_message = '_Пользователю <@{0}> нужно отлучиться_ `"{1}"`'.format(
            data.get('user_id'),
            data.get('text')
        )
        resp = slack_client.api_call(
            'chat.postMessage',
            channel=chanel,
            text=ask_message,
            as_user=True,
            link_names=True,
        )
        LeaveMessage.objects.create(
            author_name=data.get('user_name'),
            author_id=data.get('user_id'),
            ts=resp['ts'],
            channel=resp['channel'],
            text=data.get('text'),
            team=team
        )
        return HttpResponse('Your asking was received.')
    else:
        raise PermissionDenied


@csrf_exempt
@require_POST
def take_event_view(request):
    data = json.loads(request.body.decode())
    if data.get('token') == settings.VERIFICATION_TOKEN:
        if data.get('challenge'):
            return HttpResponse(data.get('challenge'))
        elif data.get('event').get('thread_ts'):
            try:
                event = data.get('event')
                ask_message = LeaveMessage.objects.get(ts=event.get('thread_ts'))
                AnswerMessage.objects.create(
                    author_id=event.get('user'),
                    ts=event.get('ts'),
                    text=event.get('text'),
                    ask_message=ask_message
                )
                slack_client = SlackClient(settings.SLACK_BOT_TOKEN)
                resp = slack_client.api_call(
                    'conversations.open',
                    users=ask_message.author_id
                )
                if resp['ok']:
                    print(event)
                    answer = '_На Ваш запрос(`{0}`) <@{1}> ответил_ "`{2}`"'.format(
                        ask_message.text,
                        event.get('user'),
                        event.get('text')
                    )
                    slack_client.api_call(
                        'chat.postMessage',
                        channel=resp['channel']['id'],
                        text=answer,
                        as_user=True,
                        link_names=True,
                    )
                ask_message.is_answered = True
            except:
                pass
        return HttpResponse()
    raise PermissionDenied


@login_required(
    login_url='https://slack.com/oauth/authorize?scope=bot&client_id={0}'.format(settings.CLIENT_ID)
)
def logout_view(request):
    logout(request)
    return redirect('slack:list_team')


class ListTeam(ListView):
    template_name = 'list_team.html'
    model = Team
    context_object_name = 'team'

    def get_queryset(self):
        if not isinstance(self.request.user, AnonymousUser):
            return Team.objects.filter(users=self.request.user)
        else:
            return Team.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListTeam, self).get_context_data(**kwargs)
        client_id = settings.CLIENT_ID
        context['client_id'] = client_id
        return context


class BotSettings(DetailView, FormMixin):
    template_name = 'settings.html'
    model = Team
    form_class = TeamChannelsForm
    context_object_name = 'team'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super(BotSettings, self).get_context_data(**kwargs)
        channels_team = Channels.objects.filter(team=self.get_object())
        active_chanel = [ch for ch in channels_team if ch.active_chanel]
        if active_chanel:
            context['active_chanel'] = active_chanel[0]
        else:
            context['active_chanel'] = None
        return context

    def get_form_kwargs(self):
        team = self.get_object()
        return {'team': team}

    def post(self, request, *args, **kwargs):
        team = self.get_object()
        data = request.POST
        new_active_chanel = data['channels']
        channels = Channels.objects.filter(team=team)
        for ch in channels:
            if ch.active_chanel:
                ch.active_chanel = False
                ch.save()
        chanel = Channels.objects.get(chanel_name=new_active_chanel)
        chanel.active_chanel = True
        chanel.save()
        return redirect('slack:bot_settings', team.slug)


class BotStatistics(DetailView):
    template_name = 'statistics.html'
    model = Team
    context_object_name = 'team'
    slug_url_kwarg = 'slug'


class AddModer(FormView):
    template_name = 'moderator.html'
    form_class = SendMessage
    success_url = '/slack/list_team/'

    def form_valid(self, form):
        form.send_email()
        return super(AddModer, self).form_valid(form)
