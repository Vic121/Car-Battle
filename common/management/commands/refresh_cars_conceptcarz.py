# -*- coding: utf-8 -*-
import re
from urllib2 import Request, urlopen, URLError, HTTPError

from django.core.management.base import NoArgsCommand

from common.models import Car, CarDetail


# from lxml import etree, html
from BeautifulSoup import BeautifulSoup
import simplejson as json


class CarRefresh(object):
    def __init__(self):
        self.online = True  # not settings.LOCAL
        self.csv_loc = '/home/marek/conceptcarz.csv'

    # --- Fetch
    def _fetch(self, url=None):
        if url is None: url = self.url

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

    # def fetch_manufs(self):
    # 	print 'fetching manufacturers'
    # 	if self.online: self.url = 'http://www.data4car.com/manufacturers.php'
    # 	else: 			self.url = '/Users/marek/Sites/cars/static/xmanufacturers.html'
    # 	self.manufs_tree = BeautifulSoup(self._fetch())
    #
    # def fetch_models(self, url):
    # 	print 'fetching models for manufacturer %s' % url
    # 	if self.online: self.url = url
    # 	else:			self.url = '/Users/marek/Sites/cars/static/xmanufacturer.html'
    # 	self.models_tree = BeautifulSoup(self._fetch())

    def fetch_model(self, url):
        if self.online:
            self.url = url
        else:
            self.url = '/Users/marek/Downloads/car.html'
        print 'fetching model %s' % self.url
        self.model_tree = BeautifulSoup(self._fetch())

    # --- Parse
    # def parse_manufs(self):
    # 	self.manufs = {}
    #
    # 	for tag in self.manufs_tree.findAll('a', attrs={'href': re.compile('^\/Car_Manufacturer\/.+')}):
    # 		if not tag.font: continue
    # 		# v, k = re.findall('^\/Car_Manufacturer\/(.+)\/(\d+)$', tag['href'])[0]
    # 		self.manufs[tag.font.b.string.strip()] = 'http://www.data4car.com' + tag['href']
    # 	print 'found %d' % len(self.manufs)
    #
    # def parse_models(self):
    # 	self.models = {}
    #
    # 	for tag in self.models_tree.findAll('a', attrs={'href': re.compile('^\/.*\/\d+$')}):
    # 		# v = re.findall('^\/.*\/(\d+)$', tag['href'])[0]
    # 		if not tag.string: continue
    # 		self.models[tag.string.strip()] = 'http://www.data4car.com' + tag['href']
    #
    # 	print 'found %d' % len(self.models)

    def parse_model(self, model_id):
        self.attrs = {}

        car = Car()
        car.manuf = self.current['manuf']
        car.year = self.current['year']
        car.source = self.current['source']
        car.source_id = self.current['source_id']
        car.url = self.current['url']

        model = self.model_tree.find('h1').string
        car.model = model.replace(car.year, '').replace(car.manuf, '').replace('Specifications', '').strip()

        # Content
        last_attr = None
        skip_next = False
        for attr in self.model_tree.findAll('tr', attrs={'class': 'ratingStyle'}):
            attrs = attr.findAll('td')
            if attrs[0] is None or attrs[0].string in (None, '&nbsp;') or \
                            attrs[1] is None or attrs[1].string in (None, '&nbsp;'):
                continue
            self.attrs[attrs[0].string.strip()] = attrs[1].string.strip()

        # Parse attrs
        self.re = {
            'Horsepower': re.compile('^(\d{2,}[\.\d]*) BHP \((\d{1,}[\.\d]*) KW\) @ (\d{4,5}) RPM$'),
            'Horsepower 2': re.compile('^(\d{2,}[\.\d]*) BHP \((\d{1,}[\.\d]*) KW\)$'),
            'Torque': re.compile('\((\d{2,}[\.\d]*)\) NM.*(\d{4,5}) RPM$'),
            'Torque 2': re.compile('\((\d{2,}[\.\d]*)\) NM$'),
            'Size': re.compile('\| (\d{3,5}) mm'),
            'Weight': re.compile('\| (\d{3,5}) kg$'),
            'Sprint': re.compile('^(\d{1,3}[\.\d]*) s'),
            'Top Speed': re.compile('\| (\d{2,3})[\.\d]* km/h'),
            'Power-to-weight': re.compile('^(\d{1,}[\.\d]*) bhp/ton$'),
            'Cylinders': re.compile('^(\w{1}-\d{1,2})'),
            'Fuel capacity': re.compile('(\d{2,4})[\.\d]* litres'),
            'Fuel consumption': re.compile('^(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)/(\d{1,}[\.\d]*)'),
            'Displacement': re.compile('^(\d{3,5}[\.\d]*) cc | \d[\.\d]* cu in\. | (\d+\[.\d]*) L\.$'),
        }

        for k, v in self.attrs.iteritems():
            if k.startswith('Horsepower'):
                car.power_bhp, car.power_kw, car.power_rpm = self.re_and_find(k, v, (0, 0, 0))
                if car.power_bhp == 0 and car.power_kw == 0 and car.power_rpm == 0:
                    car.power_bhp, car.power_kw = self.re_and_find(k + ' 2', v, (0, 0))
            elif k.startswith('Torque'):
                car.torque_nm, car.torque_rpm = self.re_and_find(k, v, (0, 0))
                if car.torque_nm == 0 and car.torque_rpm == 0:
                    car.torque_nm = self.re_and_find(k + ' 2', v)
            elif k == 'Width':
                car.width = self.re_and_find('Size', v)
            elif k == 'Height':
                car.height = self.re_and_find('Size', v)
            elif k == 'Length':
                car.length = self.re_and_find('Size', v)
            elif k == 'Weight':
                car.weight = self.re_and_find('Weight', v)
            elif k in ('0-60 mph', '0-100 km/h'):
                car.sprint_0_100 = self.re_and_find('Sprint', v)
            elif k == '0-50 mph (80 km/h)':
                car.sprint_0_80 = self.re_and_find('Sprint', v)
            elif k == '0-100 mph':
                car.sprint_0_180 = self.re_and_find('Sprint', v)
            elif k == '0-200 km/h':
                car.sprint_0_200 = self.re_and_find('Sprint', v)
            elif k == 'Top Speed':
                car.top_speed = self.re_and_find(k, v)
                if car.top_speed == 249: car.top_speed = 250  # limited
            elif k == 'Type':
                car.type = v
            elif k == 'Doors':
                car.doors = v
            elif k == 'Engine Location':
                car.engine_location = v
            # elif k == 'Power-to-weight':
            # car.power_to_weight = self.re_and_find(k, v)
            elif k == 'Cylinders':
                car.cylinders = v
            # elif k == 'Fuel Capacity':
            # car.fuel_cap = self.re_and_find(k, v)
            elif k == 'Fuel consumption':
                car.fuel_max, car.fuel_min, car.fuel_avg = self.re_and_find(k, v, (0, 0, 0))
            elif k == 'Drive Type':
                if v == 'Front Wheel':
                    car.drive = 'FWD'
                elif v == 'Rear Wheel':
                    car.drive = 'RWD'
                else:
                    car.drive = v[:3]
            elif k == 'Displacement':
                car.engine, car.engine_up = self.re_and_find(k, v, (0, 0))

        car.name = car.model[:50]
        car.short_name = car.model[:25]
        if self.attrs.has_key('Tuner'):
            car.tuner = self.attrs['Tuner']
        try:
            car.engine_up = "%.1f %s%s" % (
                (int(car.engine) / 1000.0), self.attrs['Engine Configuration'], self.attrs['Cylinders'])
        except:
            pass

        if Car.objects.filter(manuf=car.manuf, model=car.model, year=car.year, doors=car.doors,
                              to_refresh=False).count() > 0:
            print 'car already in database. skip.'
            return

        car.save()

        car_d, c = CarDetail.objects.get_or_create(car=car)
        car_d.attr = json.dumps(self.attrs)
        car_d.save()

    def re_and_find(self, k, v, default=0):
        try:
            return self.re[k].findall(v)[0]
        except IndexError:
            return default

    def start(self):
        import csv

        for manuf, year, url in csv.reader(open(self.csv_loc, "rb"), delimiter=';'):
            model_id = int(re.findall('^.*carID=(\d+)', url)[0])

            self.current = {}
            self.current['manuf'] = manuf
            self.current['year'] = year
            self.current['url'] = url
            self.current['source'] = 'conceptcarz'
            self.current['source_id'] = model_id

            found = Car.objects.filter(source='conceptcarz', source_id=model_id, to_refresh=False).count()
            if found > 0: continue
            self.fetch_model(url)
            self.parse_model(model_id)


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        r = CarRefresh()
        r.start()
