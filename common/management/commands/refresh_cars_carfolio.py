# -*- coding: utf-8 -*-
import re
from urllib2 import Request, urlopen, URLError, HTTPError

from django.core.management.base import NoArgsCommand
from django.conf import settings

from common.models import Car, CarDetail


# from lxml import etree, html
from BeautifulSoup import BeautifulSoup
import simplejson as json


class CarRefresh(object):
    def __init__(self):
        self.online = not settings.LOCAL

    # --- Fetch
    def _fetch(self, url=None):
        if url is None: url = self.url

        if Car.objects.filter(url=url, to_refresh=False).count() > 0:
            print 'skip'
            return ''

        if self.online:
            req = Request(url)
            req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
            try:
                response = urlopen(req)
            except HTTPError, e:
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            except URLError, e:
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            else:
                # everything is fine
                return response.read()

        else:
            f = open(url)
            return f.read()

    def fetch_models(self, url):
        if self.online:
            self.url = url
        else:
            self.url = '/Users/marek/Sites/static/gta/r_list1.html'
        print 'fetching models at %s' % self.url
        self.models_tree = BeautifulSoup(self._fetch())

    def fetch_model(self, url):
        if self.online:
            self.url = url
        else:
            self.url = '/Users/marek/Sites/static/gta/r_car1.html'
        print 'fetching model at %s' % self.url
        self.model_tree = BeautifulSoup(self._fetch())

    # --- Parse
    def parse_models(self):
        self.models = {}

        r = re.compile('specifications\/models\/car\/\?car=(\d+)')
        for tag in self.models_tree.findAll('a', attrs={'href': re.compile('specifications\/models\/car\/\?car=\d+')}):
            k = r.findall(tag['href'])[0]
            if not tag['href'].startswith('http://'): tag['href'] = 'http://www.carfolio.com' + tag['href']
            self.models[str(k)] = tag['href']

        print 'found %d' % len(self.models)

    def _loop_params(self, content):
        ret = []
        for item in content:
            if isinstance(item, basestring):
                ret.append(item.replace('<strong>', '').replace('</strong>', ''))
                continue
            # recursive check
            ret.extend(self._loop_params(item.contents))

        return filter(lambda x: x not in ('\n'), ret)

    def parse_model(self, model_id):
        self.attrs = {}

        # Header
        try:
            year, model = \
                re.findall('(\d{4}) (.*) Technical specifications', self.model_tree.find('h1').string.strip())[0]
        except Exception, e:
            return

        self.attrs = {}
        for rows in self.model_tree.findAll('tr'):
            if not rows.find('th') or not rows.find('td'): continue
            th = self._loop_params(rows.find('th').contents)
            td = self._loop_params(rows.find('td').contents)

            if not isinstance(th, basestring): th = ' '.join(th)
            if not isinstance(td, basestring): td = ' '.join(td)

            self.attrs[th] = td

        car = Car()
        car.year = year
        car.model = model
        car.source = 'carfolio'
        car.source_id = model_id or 0
        car.url = self.url

        # Parse attrs
        self.re = {
            'Maximum power': re.compile(
                '^\d{2,}[\.\d]*[ ]+PS[ ]+\((\d{1,}[\.\d]*)[ ]+bhp[ ]+\)[ ]+\([ ]*(\d{1,}[\.\d]*)[ ]+kW[ ]+\)[ ]*@[ ]*(\d{4,5})[ ]+rpm$'),
            'Maximum power 2': re.compile(
                '^\d{2,}[\.\d]*[ ]+PS[ ]+\((\d{1,}[\.\d]*)[ ]+bhp\)[ ]+\((\d{1,}[\.\d]*)[ ]+kW\)'),
            'Maximum torque': re.compile('^(\d{2,}[\.\d]*)[ ]+Nm.*(\d{4,5})[ ]+rpm$'),
            'Maximum torque 2': re.compile('^(\d{2,}[\.\d]*)[ ]+Nm'),
            'Width': re.compile('^(\d{3,5})[ ]+mm'),
            'Length': re.compile('^(\d{3,5})[ ]+mm'),
            'Height': re.compile('^(\d{3,5})[ ]+mm'),
            'Weight': re.compile('^(\d{3,5})[ ]+kg'),
            'Sprint': re.compile('^(\d{1,3}[\.\d]*)[ ]+s'),
            'Top speed': re.compile('^(\d{3,5})[ ]+km/h'),
            'Power-to-weight': re.compile('^(\d{1,}[\.\d]*)[ ]+bhp/ton$'),
            'Cylinders': re.compile('^(\w{1}-\d{1,2})'),
            'Fuel capacity': re.compile('(\d{2,4})[\.\d]*[ ]+litres'),
            'Fuel consumption': re.compile('^(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)'),
            'CO 2  Emissions': re.compile('(\d{1,}[\.\d]*)[ ]+([\w\/]+)$'),
            'Displacement': re.compile('^(\d{1,2}[\.\d]*)[ ]+litre[ ]*(\d{3,5})[ ]+cc'),
        }

        for k, v in self.attrs.iteritems():
            if k == 'Manufacturer':
                car.manuf = v
            elif k.startswith('Maximum power'):
                try:
                    car.power_bhp, car.power_kw, car.power_rpm = self.re_and_find('Maximum power', v, (0, 0, 0))
                except IndexError:
                    try:
                        car.power_bhp, car.power_kw = self.re_and_find('Maximum power 2', v, (0, 0))
                    except IndexError:
                        pass
            elif k.startswith('Maximum torque'):
                try:
                    car.torque_nm, car.torque_rpm = self.re_and_find('Maximum torque', v, (0, 0))
                except IndexError:
                    try:
                        car.torque_nm = self.re_and_find('Maximum torque 2', v)
                    except IndexError:
                        pass
            elif k == 'Kerb weight':
                car.weight = self.re_and_find('Weight', v)
            elif k in ('0-100 km/h', '0-100  km/h'):
                car.sprint_0_100 = self.re_and_find('Sprint', v)
            elif k == 'Power-to-weight':
                car.power_to_weight = self.re_and_find(k, v, 0)
            elif k == 'Top speed':
                car.top_speed = self.re_and_find(k, v)
            elif k == 'Number of doors':
                car.doors = v
            elif k == 'Fuel capacity':
                car.fuel_cap = self.re_and_find(k, v)
            elif k == 'Fuel consumption':
                car.fuel_max, car.fuel_min, car.fuel_avg = self.re_and_find(k, v, (0, 0, 0))
            elif k == 'CO 2  Emissions':
                car.co2, car.co2_unit = self.re_and_find(k, v, (0, 0))
            elif k == 'Drive':
                car.drive = v[:3]
            elif k == 'Displacement':
                car.engine_up, car.engine = self.re_and_find(k, v, (0, 0))
            elif k == 'Engine location':
                car.engine_location = v
            elif k == 'Type':
                car.type = v[:v.index(' ')]
            elif self.re.has_key(k):
                car.__dict__[k.lower()] = self.re_and_find(k, v)

        if Car.objects.filter(manuf=car.manuf, model=car.model, year=car.year, doors=car.doors,
                              to_refresh=False).count() > 0:
            print 'car already in database. skip.'
            return

        car.name, car.short_name = car.model, car.model

        try:
            car.save()
        except Exception, e:
            print 'car error', e
            return

        car_d, c = CarDetail.objects.get_or_create(car=car)
        car_d.attr = json.dumps(self.attrs)
        car_d.save()

    def re_and_find(self, k, v, default=0):
        try:
            return self.re[k].findall(v)[0]
        except IndexError:
            return default
        except TypeError, e:
            print e
            raise

    def start(self):
        print '--- Parsing Latest Models ---'
        self.fetch_models('http://carfolio.com/search/results/?makematch=c&modelmatch=c&y1=2010&num=1000&offset=0')
        self.parse_models()

        print '--- Models ---'
        for model_id, url in self.models.iteritems():
            found = Car.objects.filter(source='carfolio', url=url, to_refresh=False).count()
            if found > 0:
                print 'skip'
                continue
            self.fetch_model(url)
            self.parse_model(model_id)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        r = CarRefresh()
        r.start()
