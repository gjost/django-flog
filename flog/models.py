"""flog - a life log

Make an easy web interface for tracking what you're eating, when, how much.
Nice easy mobile-friendly data entry form.

"""
from datetime import date, datetime, timedelta
from optparse import OptionParser

from django.conf import settings
from django.db import models

from tagging.models import Tag
from tagging.fields import TagField


swallop = OptionParser()
swallop.prog = 'swallo'
swallop.usage = '%prog [options]'
swallop.add_option("-a", "--amt", dest="amount",)
swallop.add_option("-c", "--cal", dest="calories")
swallop.add_option("-t", "--tag", dest="tags")
swallop.add_option("-m", "--memo", dest="description")

weighp = OptionParser()
weighp.add_option("-e", "--empty", dest="empty")
weighp.add_option("-m", "--memo", dest="description")

entry_help_text = swallop.usage

ENTRY_HELP_TEXT = "swallo ITEM [-a/--amt '3 biscuits'][-c/--cal 240][-t/--tag bkfst][-m]<br/>" \
                  "weigh 150lb [-e/--empty]<br/>" \
                  "woke 1015 [-m]<br/>" \
                  "slept 2345 [-m]<br/>" \
                  "p [1=[s,m,l],[1,2,3]] [2=[[s,m,l],[1,2,3]] [-m]<br/>" \
                  "NOTE: Separate multiple entries with semicolons<br/>"




class Day(models.Model):
    """A place to keep daily summary info so doesn't have to be recalculated all the time.
    """
    date = models.DateField(primary_key=True)
    incomplete = models.BooleanField()
    weight = models.FloatField("Weight (kg)", blank=True, null=True)
    weight_empty = models.BooleanField()
    calories = models.IntegerField(blank=True, null=True)
    hours_slept = models.CharField(max_length=10, blank=True, null=True)
    coffee_cups = models.IntegerField(blank=True, null=True)
    coffee_oz = models.IntegerField(blank=True, null=True)
    p1 = models.IntegerField(blank=True, null=True)
    
    class Meta:
        get_latest_by = 'date'
        ordering = ['-date']
        permissions = (
            ("can_flog_day", "Can create flog days"),
        )
    
    def get_absolute_url(self):
        return '/flog/%s/' % self.date.strftime('%Y/%m/%d')
    
    def __unicode__(self):
        return '%s' % self.date
    
    def save(self, *args, **kwargs):
        """Recalculate the stats for the Day on save().
        """
        sod = datetime(self.date.year, self.date.month, self.date.day, 0,0,0)
        eod = datetime(self.date.year, self.date.month, self.date.day, 23,59,59)
        entries = Entry.objects.filter(created__gte=sod, created__lte=eod)
        swallows = Swallow.objects.filter(created__gte=sod, created__lte=eod)
        
        # summary info -------------------------------
        # incomplete
        for e in entries:
            if (e.txt.find('incomplete') != -1):
                self.incomplete = True
        # calories ---------------------
        self.calories = 0
        for s in swallows:
            if s.calories:
                self.calories = self.calories + s.calories
        # cups of coffee ---------------
        self.coffee_cups = 0
        for s in swallows:
            if (s.title.find('coffee') != -1) or (s.tags.find('coffee') != -1):
                self.coffee_cups = self.coffee_cups + 1
        # weight -----------------------
        self.weight = None
        self.weight_empty = False
        for e in entries:
            if (e.txt.find('weigh') != -1):
                parts = e.txt.split(' ')
                try:
                    if e.txt.find('lb') != -1:
                        # convert to kg
                        w = parts[1].replace('lb','')
                        self.weight = w/2.2
                    else:
                        self.weight = parts[1].replace('lb','')
                    # emptyweight
                    if e.txt.find('-e') != -1:
                        self.weight_empty = True
                except:
                    pass
        # hours of sleep ---------------
        self.hours_slept = None
        def parse_time(txt):
            try:
                parts = txt.split(' ')
                hhmm = parts[1].split(':')
                return datetime(sod.year, sod.month, sod.day, int(hhmm[0]), int(hhmm[1]))
            except:
                return None
        sleep_time = None
        wake_time = None
        for e in entries:
            if e.txt.find('wake') != -1:
                wake_time = parse_time(e.txt)
            elif e.txt.find('sleep') != -1:
                # sometimes go to sleep after midnight :)
                sleep_time = parse_time(e.txt)
        if wake_time and not sleep_time:
            # went to sleep before midnight
            sod_prev = sod - timedelta(1)
            eod_prev = eod - timedelta(1)
            yesterday = Entry.objects.filter(created__gte=sod_prev,
                                             created__lte=eod_prev)
            for e in yesterday:
                if e.txt.find('sleep') != -1:
                    sleep_time = parse_time(e.txt)
        if wake_time and sleep_time:
            td = wake_time - sleep_time
            hours = td.seconds // 3600
            minutes = (td.seconds % 3600) // 60
            self.hours_slept = '%s:%s' % (hours, minutes) 
        # p1,p2 ------------------------
        self.p1 = 0
        for e in entries:
            if (e.txt.find('p ') != -1) and (e.txt.find('1=') != -1):
                self.p1 = self.p1 + 1
        # Done!
        super(Day, self).save(*args, **kwargs)

    def weight_lbs(self):
        """
        """
        if self.weight:
            return self.weight * 2.2
        else:
            return None

    def get_sparkline_data(self):
        """Get Day data for the last 30days.
        """
        last30days = Day.objects.filter(
            date__lte=self.date).order_by('-date')[:30]
        self.sparkline_weight = []
        self.sparkline_calories = []
        self.sparkline_sleep = []
        self.sparkline_coffee_cups = []
        self.sparkline_p1 = []
        [self.sparkline_weight.append(d.weight) for d in last30days if d.weight]
        [self.sparkline_calories.append(d.calories) for d in last30days if d.calories]
        [self.sparkline_sleep.append(d.hours_slept) for d in last30days if d.hours_slept]
        [self.sparkline_coffee_cups.append(d.coffee_cups) for d in last30days if d.coffee_cups]
        [self.sparkline_p1.append(d.p1) for d in last30days if d.p1]


class Entry(models.Model):
    """An individual flog entry.
    
    Flog entry form. Syntax is in txt.help_text.
    """
    #user
    created = models.DateTimeField(blank=True, null=True)
    txt = models.CharField(max_length=255,
#        help_text=entry_help_text
        help_text="swallo ITEM [-a/--amt '3 biscuits'][-c/--cal 240][-t/--tag bkfst][-m]<br>"
                  "weigh 150lb [-e/--empty]<br>"
                  "woke 1015 [-m]<br>"
                  "slept 2345 [-m]<br>"
                  "p [1=[s,m,l],[1,2,3]] [2=[[s,m,l],[1,2,3]] [-m]<br>"
                  "NOTE: Separate multiple entries with semicolons<br>"
                  "NOTE: <br>"
    )
    
    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        permissions = (
            ("can_flog_entry", "Can create flog entries"),
        )
    
    def get_absolute_url(self):
        return '/flog/%s/%d/' % (self.created.strftime('%Y/%m/%d'), self.id)
    
    def __unicode__(self):
        return '(%s) %s' % (self.created, self.txt,)
    
    def save(self, *args, **kwargs):
        """If posting is published, generate a datamatrix when saving.
        """
        if not self.id:
            self.created = datetime.now()
            self.process()
        super(Entry, self).save(*args, **kwargs)
        # create/update Day record
        d = date(self.created.year, self.created.month, self.created.day)
        try:
            day = Day.objects.get(date=d)
        except Day.DoesNotExist:
            day = Day(date=d)
        day.save()
    
    def delete(self):
        super(Entry, self).delete()
    
    def process(self):
        """Examine self.txt and create a Swallow or some other type

        Uses optparse

        PROBLEM: optparse.parse_args() expects a list like sys.argv[1:].
        Right now, all I know is to split() the txt on spaces, which breaks up memos with spaces.
        Would be nice to have a regex that changes all spaces within quotes to something else.
        """
        txts = self.txt.split(';')
        for txt in txts:
            txt = txt.strip()
            parts = txt.split(' ')
            # Swallow
            if parts[0] and (parts[0] == 'swallo'):
                (options, args) = swallop.parse_args(args=quoted_split(self.txt)[1:])
                sw = Swallow(title = args[0],
                             tags = options.tags,
                             calories = options.calories,
                             serving_size = options.amount,
                             description = options.description,)
                sw.save()
            #
            elif parts[0] and (parts[0] == 'weigh'):
                (options, args) = weighp.parse_args(args=self.txt.split(' ')[1:])

def quoted_split(txt):
    """Splits a string of text, but keeps quoted strings together.
    
    >>> smart_split("swallo wheatabix -a '3 biscuits + soy milk' -c 240 -t bkfst")
    ['swallo', 'wheatabix', '-a', '3 biscuits + soy milk', '-c', '240', '-t', 'bkfst']
    """
    # change all single- or double-quoted spaces with carats
    new = [] # build new string as list
    squoted = 0
    dquoted = 0
    for i in range(len(txt)):
        if txt[i]=="'":
            squoted = squoted + 1
        elif txt[i]=='"':
            dquoted = dquoted + 1
        elif (txt[i]==' ') and ((squoted%2) or (dquoted%2)):
            new.append('^')
        else:
            new.append(txt[i])
    txt = ''.join(new) # re-joing into a string
    # split on the unquoted spaces, replacing quoted carats with spaces
    chunks = []
    [chunks.append(c.replace('^', ' ')) for c in txt.split(' ')]
    return chunks
    
        

class Swallow(models.Model):
    """Some piece of food.
    """
    #user
    created = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    calories = models.IntegerField(max_length=255, blank=True, null=True)
    serving_size = models.CharField(max_length=255, blank=True, null=True,
        help_text='t=tsp, T=Tbs, c=cup, oz=ounce, pt=pint, qt=quart, g, kg, lb=pound,<br>'
                  'pc=piece, pcs=pieces, pkg=package',
    )
    tags = TagField(blank=True)
    
    class Meta:
        get_latest_by = 'created'
        ordering = ['-created']
        permissions = (
            ("can_flog_swallow", "Can access food items"),
        )
    
    def get_absolute_url(self):
        return '/flog/sw/%d/' % self.id
    
    def __unicode__(self):
        return '(%s) %s' % (self.created, self.title,)
    
    def save(self, *args, **kwargs):
        """If posting is published, generate a datamatrix when saving.
        """
        if not self.id:
            self.created = datetime.now()
        super(Swallow, self).save(*args, **kwargs)
        # create/update Day record
        d = date(self.created.year, self.created.month, self.created.day)
        try:
            day = Day.objects.get(date=d)
        except Day.DoesNotExist:
            day = Day(date=d)
        day.save()
    
    def delete(self):
        super(Swallow, self).delete()
    


#class Weight(models.Model):
#    """The user's weight at a given point in time.
#    """
#    #user
#    created = models.DateTimeField()
#    weight = models.IntegerField()
#    notes = models.TextField(blank=True, null=True)
