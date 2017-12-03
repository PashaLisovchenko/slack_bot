from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Team(models.Model):
    team_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=20, null=True, blank=True)
    team_id = models.CharField(max_length=20)
    admin = models.ForeignKey(User, related_name='admin_teams', null=True)
    users = models.ManyToManyField(User, related_name='users_team')

    def __str__(self):
        return self.team_name

    def get_absolute_url(self):
        return reverse('slack:bot_settings',
                       args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.team_id)
        super(Team, self).save(*args, **kwargs)


class Channels(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='channels')
    chanel_name = models.CharField(max_length=100, null=True)
    active_chanel = models.BooleanField(default=False)

    def __str__(self):
        return self.team.team_name+"__"+self.chanel_name


class LeaveMessage(models.Model):
    author_name = models.CharField(max_length=200)
    author_id = models.CharField(max_length=20)
    ts = models.CharField(max_length=40)
    channel = models.CharField(max_length=20)
    text = models.TextField()
    create_date = models.DateField(auto_now=False, auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='ask_messages')

    def __str__(self):
        return self.text


class AnswerMessage(models.Model):
    author_id = models.CharField(max_length=20)
    ts = models.CharField(max_length=40)
    text = models.TextField()
    create_date = models.DateField(auto_now=False, auto_now_add=True)
    ask_message = models.ForeignKey(LeaveMessage, on_delete=models.CASCADE, related_name='answer_messages')

    def __str__(self):
        return self.text
