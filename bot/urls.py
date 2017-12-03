from django.conf.urls import url
from .views import slack_oauth_view, take_ask_message_view, take_event_view, logout_view, ListTeam, BotSettings,\
    BotStatistics, AddModer

urlpatterns = [
    url(r'^oauth/$', slack_oauth_view, name='slack_oauth'),
    url(r'^message/$', take_ask_message_view),
    url(r'^events/$', take_event_view),

    url(r'^list_team/$', ListTeam.as_view(), name='list_team'),

    url(r'^settings/(?P<slug>[-\w]+)/$', BotSettings.as_view(), name='bot_settings'),
    url(r'^statistics/(?P<slug>[-\w]+)/$', BotStatistics.as_view(), name='bot_statistics'),
    url(r'^add_moder/$', AddModer.as_view(), name='add_moder'),
    url(r'logout/$', logout_view, name='logout'),
]
