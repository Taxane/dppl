from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from apps.abstract.models import CommonModel
from apps.accounts.elo import rank


class Division(CommonModel):
    """ The division.  Right now, there are two, Honey and Badger.
    """
    name = models.CharField(_("Name"), max_length=255)
    # Leagues can have divisions w/ the same name
    slug = models.SlugField(_("Slug"), max_length=255)

    # Relations
    league = models.ForeignKey("League")

    class Meta:
        ordering = ("-name",)

    def __unicode__(self):
        return self.name


class Game(CommonModel):
    """ The game.
    """
    WINNER_CHOICES = ((1, "Player 1",), (2, "Player 2"),)

    winner = models.CharField(_("Winner"), choices=WINNER_CHOICES,
            max_length=1, null=True, blank=True)
    # Relations
    match = models.ForeignKey("Match")
    player1 = models.ForeignKey(User, related_name="user1")
    player2 = models.ForeignKey(User, related_name="user2")

    def set_rank(self):
        """ This will rank players one and two based on the outcome. """
        if self.winner == 1:
            self.player1, self.player2 = rank(self.player1, self.player2)
        else:
            self.player2, self.player1 = rank(self.player2, self.player1)
        self.player1.save()
        self.player2.save()


class League(CommonModel):
    """  This is the league.  It won't really get used except if we go global.
         Which we will.
    """
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)

    def current_seasons(self):
        return self.season_set.filter(go_live_date__lte=datetime.now())\
            .filter(go_dead_date__gte=datetime.now())

    @property
    def current_season(self):
        season = self.season_set.exclude(go_live_date__gt=datetime.now())\
                .order_by('-go_live_date')[:1]
        return season[0] if len(season) > 0 else None

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name


class Match(CommonModel):
    """ The match.
    """
    team1_score = models.IntegerField(blank=True, null=True,
        help_text=_("Set the score to mark the match completed."))
    team2_score = models.IntegerField(blank=True, null=True,
        help_text=_("Set the score to mark the match completed."))

    # Relations
    round = models.ForeignKey("Round")
    division = models.ForeignKey("Division")
    team1 = models.ForeignKey("Team", related_name="team1", help_text=_("Home Team"))
    team2 = models.ForeignKey("Team", related_name="team2", help_text=_("Away Team"))

    @property
    def loser(self):
        if self.team1_score is None:
            return None
        return self.team1 if self.team1_score < self.team2_score else self.team2

    @property
    def winner(self):
        if self.team1_score is None:
            return None
        return self.team1 if self.team1_score > self.team2_score else self.team2

    @property
    def winning_score(self):
        return self.team1_score if self.team1_score > self.team2_score else self.team2_score

    @property
    def scored_match(self):
        if self.round.in_past() and self.team1_score is not None and self.team2_score is not None:
            return "%s %s v %s %s" % (self.team1.abbr, self.team1_score,\
                                      self.team2.abbr, self.team2_score)
        return self

    class Meta:
        verbose_name_plural = "Matches"
        ordering = ("division", "round",)

    def __unicode__(self):
        return "%s v %s" % (self.team1.abbr, self.team2.abbr)


class Round(CommonModel):
    """ The round, as in 'Round 1, FIGHT!'
    """
    name = models.CharField(_("Name"), max_length=255)
    short_name = models.CharField(_("Short Name"), max_length=1)
    go_live_date = models.DateTimeField(_("Go Live Date"))
    go_dead_date = models.DateTimeField(_("Go Dead Date"))

    # Relations
    season = models.ForeignKey("Season")

    def in_past(self):
        return self.go_dead_date < datetime.now()

    def current(self):
        now = datetime.now()
        return self.go_live_date <= now and self.go_dead_date >= datetime.now()

    def division_matches(self, division_id):
        return self.match_set.filter(division=Division.objects.get(pk=division_id))

    class Meta:
        ordering = ("go_live_date",)

    def __unicode__(self):
        return "%s - %s" % (self.season, self.name)


class Season(CommonModel):
    """ The season.
    """
    name = models.CharField(_("Name"), max_length=255)
    # Don't make this unique because leagues can have seasons w/ the same name.
    slug = models.SlugField(_("Slug"), max_length=255)
    go_live_date = models.DateField(_("Go Live Date"))
    go_dead_date = models.DateField(_("Go Dead Date"), blank=True, null=True)

    # Relations
    league = models.ForeignKey("League")

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name


class Team(CommonModel):
    """ The team model.
    """
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)
    abbr = models.CharField(_("Abbr"), max_length=5)
    website = models.URLField(blank=True, null=True, verify_exists=False)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=255, blank=True)
    state = models.CharField(_("State"), max_length=2, blank=True)
    zip_code = models.CharField(_("Zip Code"), max_length=20, blank=True)
    description = models.TextField(_("Description"), blank=True)
    contact_name = models.CharField(_("Contact Name"), max_length=255, blank=True)
    contact_email = models.CharField(_("Contact Email"), max_length=255, blank=True)

    # Relations
    division = models.ForeignKey(Division)

    def current_schedule(self, season):
        if season is None:
            return None
        return self.division.match_set.filter(round__season=season)\
                   .filter(Q(team1=self) | Q(team2=self))

    @property
    def name_and_abbr(self):
        if self.name == self.abbr:
            return self.name
        return "%s (%s)" % (self.name, self.abbr)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('theleague_team', [str(self.slug)])


