#!/usr/bin/python
import os

import sys

sys.path.append('/Users/marek/Sites/')
sys.path.append('/home/marek/')
os.environ["DJANGO_SETTINGS_MODULE"] = 'crimecorp.settings'

# import logging
# from userprofile.models import UserProfile

if __name__ == '__main__':

    # for user in UserProfile.objects.all():
    # 	sql = """INSERT INTO task (user_id, source, task, comment, created_at) VALUES ("%s", "%s", "", "", "%s")""" % (str(user.user.id), 'city', str(datetime.datetime.now()))
    #
    # 	cursor = connection.cursor()
    # 	cursor.execute(sql)
    # 	connection.connection.commit()

    from crimecorp.item.models import Item, Garage, Car
    from crimecorp.auction.models import Auction
    import simplejson as json

    for auction in Auction.objects.all():
        item = Item.objects.filter(image_filename=auction.image_filename)[0]
        details = json.loads(item.details)
        details['product_id'] = item.id
        auction.details = json.dumps(details)
        auction.save()

    for garage in Garage.objects.all():
        new_garage = []
        for car in garage.items:
            c = Car.objects.get(pk=car)
            i = Item.objects.get(name=c.name)
            new_garage.append(str(i.id))
        garage.item = ','.join(new_garage)
        garage.save()
