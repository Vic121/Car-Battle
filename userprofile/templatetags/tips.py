# -*- coding: utf-8 -*-
from django.template.loader import render_to_string
from django.template import Library
from django.conf import settings

from common.helpers.core import reverse

register = Library()


@register.simple_tag
def show_how_to_play(request):
    page = request.engine.module
    profile = request.engine.user.profile

    if page not in settings.HOW_TO_PLAY: return ''
    if profile.how_to_play_status(settings.HOW_TO_PLAY.index(page)) == '0':
        ret = """
			<script type="text/javascript">
			function confirm_close() {
				$.post('%s', {'page': '%s'}, function(data) {
					$('#how_to_play').slideUp();
				});
			}
			</script>
		""" % (reverse('confirm_close'), page)
        ret += '<div id="how_to_play">'
        ret += '<div class="menu">'
        ret += '<div class="close"><a href="#" onclick="confirm_close(); return false;">close</a></div>'
        ret += '<h3>How to Play?</h3>'
        ret += render_to_string('userprofile/how_to_play/' + page + '.html', {})
        ret += '</div></div>'
        return ret
    return ''
