# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection


@staff_member_required
def index(request):
    for uid in query(
            "SELECT a.id FROM auth_user AS a LEFT JOIN user AS u ON u.user_id=a.id WHERE (a.email LIKE '%%madfb.com' OR a.email LIKE '%%mail.ru') AND u.exp < 1000"):
        delete_user(uid[0])

    return render_to_response(
        'intranet/user.html', {

        }, context_instance=RequestContext(request)
    )


def query(query):
    cursor = connection.cursor()
    c = cursor.execute(query)
    return cursor.fetchall()


def delete_user(uid):
    """SAFETY FIRST!"""

    query("DELETE FROM auth_user WHERE id=%s" % uid)
    query("DELETE FROM auction WHERE seller_id=%s" % uid)
    query("DELETE FROM auction_offer WHERE buyer_id=%s" % uid)
    query("DELETE FROM gift WHERE sender_id=%s" % uid)
    query("DELETE FROM msg WHERE sender_id=%s OR receiver_id=%s" % (uid, uid))
    query("DELETE FROM user_gift_log WHERE from_user_id=%s OR to_user_id=%s" % (uid, uid))

    for table in (
            'auth_user_groups', 'auth_user_user_permissions', 'album_stat_user', 'job_stat_user', 'user',
            'user_achievement',
            'user_album', 'user_avatar', 'user_day_stat', 'user_detail', 'user_friend', 'user_garage', 'user_gift',
            'user_job',
            'user_mail', 'user_stat', 'user_stream', 'user_wishlist'):
        query("DELETE FROM %s WHERE user_id=%s" % (table, uid))
