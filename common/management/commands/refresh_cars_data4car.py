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

    def fetch_manufs(self):
        print 'fetching manufacturers'
        if self.online:
            self.url = 'http://www.data4car.com/manufacturers.php'
        else:
            self.url = '/Users/marek/Sites/cars/static/xmanufacturers.html'
        self.manufs_tree = BeautifulSoup(self._fetch())

    def fetch_models(self, url):
        print 'fetching models for manufacturer %s' % url
        if self.online:
            self.url = url
        else:
            self.url = '/Users/marek/Sites/cars/static/xmanufacturer.html'
        self.models_tree = BeautifulSoup(self._fetch())

    def fetch_model(self, url):
        print 'fetching model %s' % url
        if self.online:
            self.url = url
        else:
            self.url = '/Users/marek/Sites/cars/static/xcar.html'
        self.model_tree = BeautifulSoup(self._fetch())

    # --- Parse
    def parse_manufs(self):
        self.manufs = {}

        for tag in self.manufs_tree.findAll('a', attrs={'href': re.compile('^\/Car_Manufacturer\/.+')}):
            if not tag.font: continue
            # v, k = re.findall('^\/Car_Manufacturer\/(.+)\/(\d+)$', tag['href'])[0]
            self.manufs[tag.font.b.string.strip()] = 'http://www.data4car.com' + tag['href']
        print 'found %d' % len(self.manufs)

    def parse_models(self):
        self.models = {}

        for tag in self.models_tree.findAll('a', attrs={'href': re.compile('^\/.*\/\d+$')}):
            # v = re.findall('^\/.*\/(\d+)$', tag['href'])[0]
            if not tag.string: continue
            self.models[tag.string.strip()] = 'http://www.data4car.com' + tag['href']

        print 'found %d' % len(self.models)

    def parse_model(self, model_id):
        self.attrs = {}

        # Header
        try:
            model = self.model_tree.find('font', attrs={'color': '#0000ff',
                                                        'style': 'font-size: 13px;font-weight: bold;'}).string.strip()
        except:
            return

        try:
            print model
        except:
            pass

        car = Car()
        car.manuf = self.curr_manuf
        try:
            car.model, car.year = re.findall('(.+) \((\d{4})\)', model.replace(self.curr_manuf, '').strip())[0]
        except IndexError:
            return
        car.source = 'data4car'
        car.source_id = model_id or 0
        car.url = self.url

        # Content
        last_attr = None
        for attr in self.model_tree.findAll('td', attrs={'style': re.compile('background-color:#(c0c0c0|dddddd);')}):
            if attr is None or attr.string is None: continue
            attr = attr.string.strip()

            if last_attr is None:
                self.attrs[attr] = None
                last_attr = attr
            else:
                self.attrs[last_attr] = attr
                last_attr = None

        # Parse attrs
        self.re = {
            'Maximum power': re.compile(
                '^\d{2,}[\.\d]* PS \((\d{1,}[\.\d]*) bhp\) \((\d{1,}[\.\d]*) kW\)@ (\d{4,5}) rpm$'),
            'Maximum power 2': re.compile('^\d{2,}[\.\d]* PS \((\d{1,}[\.\d]*) bhp\) \((\d{1,}[\.\d]*) kW\)'),
            'Maximum torque': re.compile('^(\d{2,}[\.\d]*) Nm.*(\d{4,5}) rpm$'),
            'Maximum torque 2': re.compile('^(\d{2,}[\.\d]*) Nm'),
            'Size': re.compile('^(\d{3,5}) mm'),
            'Weight': re.compile('^(\d{3,5}) kg'),
            'Sprint': re.compile('^(\d{1,3}[\.\d]*) s'),
            'Top speed': re.compile('^(\d{3,5}) km/h'),
            'Power-to-weight': re.compile('^(\d{1,}[\.\d]*) bhp/ton$'),
            'Cylinders': re.compile('^(\w{1}-\d{1,2})'),
            'Fuel capacity': re.compile('(\d{2,4})[\.\d]* litres'),
            'Fuel consumption': re.compile('^(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)'),
            'CO2 Emissions': re.compile('(\d{1,}[\.\d]*) ([\w\/]+)$'),
            'Displacement': re.compile('^(\d{1,2}[\.\d]*) litre(\d{3,5}) cc'),
        }

        for k, v in self.attrs.iteritems():
            if k.startswith('Maximum power'):
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
            elif k == 'Width':
                car.width = self.re_and_find('Size', v)
            elif k == 'Height':
                car.height = self.re_and_find('Size', v)
            elif k == 'Length':
                car.length = self.re_and_find('Size', v)
            elif k == 'Kerb weight':
                car.weight = self.re_and_find('Weight', v)
            elif k in ('0-60 mph', '0-100 km/h'):
                car.sprint_0_100 = self.re_and_find('Sprint', v)
            elif k == '0-50 mph (80 km/h)':
                car.sprint_0_80 = self.re_and_find('Sprint', v)
            elif k == '0-100 mph':
                car.sprint_0_180 = self.re_and_find('Sprint', v)
            elif k == '0-200 km/h':
                car.sprint_0_200 = self.re_and_find('Sprint', v)
            elif k == 'Top speed':
                car.top_speed = self.re_and_find(k, v)
            elif k == 'Type':
                car.type = v
            elif k == 'Number of doors':
                car.doors = v
            elif k == 'Power-to-weight':
                car.power_to_weight = self.re_and_find(k, v)
            elif k == 'Cylinders':
                car.cylinders = self.re_and_find(k, v)
            elif k == 'Fuel capacity':
                car.fuel_cap = self.re_and_find(k, v)
            elif k == 'Fuel consumption':
                car.fuel_max, car.fuel_min, car.fuel_avg = self.re_and_find(k, v, (0, 0, 0))
            elif k == 'CO2 Emissions':
                car.co2, car.co2_unit = self.re_and_find(k, v, (0, 0))
            elif k == 'Drive':
                car.drive = v[:3]
            elif k == 'Displacement':
                car.engine_up, car.engine = self.re_and_find(k, v, (0, 0))

        # try:
        # 	print car
        # except TypeError:
        # 	pass

        if Car.objects.filter(manuf=car.manuf, model=car.model, year=car.year, doors=car.doors,
                              to_refresh=False).count() > 0:
            print 'car already in database. skip.'
            return

        try:
            car.save()
        except:
            print 'car error'

        car_d, c = CarDetail.objects.get_or_create(car=car)
        car_d.attr = json.dumps(self.attrs)
        car_d.save()

    def re_and_find(self, k, v, default=0):
        try:
            return self.re[k].findall(v)[0]
        except IndexError:
            return default

    def start(self):
        print '--- Manufacturers ---'
        self.fetch_manufs()
        self.parse_manufs()

        for manuf_name, manuf_url in self.manufs.iteritems():
            self.curr_manuf = manuf_name

            # if Car.objects.filter(manuf=manuf_name).count() > 0: continue
            # if manuf_name not in ('Alfa Romeo', 'Honda', 'Holden', 'Autobianchi', 'Audi'): continue

            print '--- %s Models ---' % manuf_name
            self.fetch_models(manuf_url)
            self.parse_models()

            print '--- Model ---'
            for model_id, url in self.models.iteritems():
                found = Car.objects.filter(source='data4car', source_id=int(re.findall('^.*\/(\d+)$', url)[0]),
                                           to_refresh=False).count()
                if found > 0: continue
                self.fetch_model(url)
                self.parse_model(model_id)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        r = CarRefresh()
        r.start()
