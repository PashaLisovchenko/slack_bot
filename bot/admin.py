from django.contrib import admin
from .models import Team, Channels, LeaveMessage, AnswerMessage


class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'team_id', 'admin']


admin.site.register(Team, TeamAdmin)
admin.site.register(Channels)
admin.site.register(LeaveMessage)
admin.site.register(AnswerMessage)
