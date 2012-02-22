from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.abstract.models import CommonModel


class Division(CommonModel):
    """ The division.  Right now, there are two, Honey and Badger.
    """
    name = models.CharField(_("Name"), max_length=255)
    # Don't make this unique because leagues can have divisions w/ the same name.
    slug = models.SlugField(_("Slug"), max_length=255)

    # Relations
    league = models.ForeignKey("League")

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name


class League(CommonModel):
    """  This is the league.  It won't really get used except if we go global.
         Which we will.
    """
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name


class Match(CommonModel):
    """ The match.
    """
    date = models.DateTimeField(_("Date"))
    team1_score = models.IntegerField(blank=True, null=True)
    team2_score = models.IntegerField(blank=True, null=True)

    # Relations
    season = models.ForeignKey("Season")
    team1 = models.ForeignKey("Team", related_name="team1")
    team2 = models.ForeignKey("Team", related_name="team2")

    class Meta:
        ordering = ("date",)
        verbose_name_plural = "Matches"

    def __unicode__(self):
        return self.name


class Season(CommonModel):
    """ The season.
    """
    name = models.CharField(_("Name"), max_length=255)
    # Don't make this unique because leagues can have seasons w/ the same name.
    slug = models.SlugField(_("Slug"), max_length=255)

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

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return self.name
