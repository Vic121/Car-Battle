function activity_points_switch(pts) {
    var points = parseInt(pts / 100);
    var times = 0;
    var colour = '';

    if (points >= 3125) {
        times = parseInt(points / 3125);
        colour = 'black';
    }
    else if (points < 3125 && points >= 625) {
        times = parseInt(points / 625);
        colour = 'red';
    }
    else if (points < 625 && points >= 125) {
        times = parseInt(points / 125);
        colour = 'blue';
    }
    else if (points < 125 && points >= 25) {
        times = parseInt(points / 25);
        colour = 'green'
    }
    else if (points < 25 && points >= 5) {
        times = parseInt(points / 5);
        colour = 'orange';
    }
    else {
        times = points;
        colour = 'grey';
    }

    if (colour == '') {
        return pts;
    }

    var html = '';
    for (var i = 0; i < times; i++) {
        html += "<img src='/static/images/dot_" + colour + ".png' style='position: relative; top: 1px;' />";
    }

    return html;
}

function mouseX(evt) {
    if (!evt) evt = window.event;
    if (evt.pageX) return evt.pageX; else if (evt.clientX)return evt.clientX + (document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft); else return 0;
}
function mouseY(evt) {
    if (!evt) evt = window.event;
    if (evt.pageY) return evt.pageY; else if (evt.clientY)return evt.clientY + (document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop); else return 0;
}

$(document).ready(function () {
    pDates();
    $(".activity_points").each(function () {
        $(this).html(activity_points_switch($(this).html()));
    });
    $(".username").hover(
        function () {
            var line = $(this);
            line.find("a:first").after("<span class='username-hover'>&nbsp;</span>");
            $("span.username-hover").click(function (event) {
                $("body").prepend("<span class='username-hover-box'>&nbsp;</span>");
                hover_box = $("span.username-hover-box");

                var _top = parseInt(mouseY(event));
                var _left = parseInt(mouseX(event));
                hover_box.css({top: _top + 10, left: _left - 100});

                $.ajax({
                    type: "GET",
                    url: "/ajax-user-box/" + line.find("a").html() + "/",
                    success: function (msg) {
                        hover_box.html(msg);
                        hover_box.find("span.hover_box_activity_points").html(
                            activity_points_switch(hover_box.find("span.hover_box_activity_points").html())
                        );
                        hover_box.click(function () {
                            hover_box.remove();
                        });
                    }
                });
            });
        },
        function () {
            $("span.username-hover").remove();
        }
    );
});

function pDates() {
    var els = document.getElementsByName('date');
    for (var i = 0, end = els.length; i < end; i++) {
        d = Date.parse(els[i].innerHTML);
        resp = get_local_time_for_date(d);
        if (resp != false) els[i].innerHTML = resp;
    }
}

// TODO: dostosowac do strony
function show_dates_as_local_time() {
    $('.typo_date').each(function () {
        $(this).html(get_local_time_for_date($(this).attr('title')));
    })
}

function get_local_time_for_date(time) {
    system_date = new Date(time);
    user_date = new Date();
    delta_minutes = Math.floor((user_date - system_date) / (60 * 1000));
    if (Math.abs(delta_minutes) <= (54 * 7 * 24 * 60)) { // up to 54 weeks
        distance = distance_of_time_in_words(delta_minutes);
        return distance + ((delta_minutes < 0) ? ' from now' : ' ago')
    } else {
        // return 'on ' + system_date.toLocaleDateString();
        return false;
    }
}

function distance_of_time_in_words(minutes) {
    if (minutes.isNaN) return "";
    minutes = Math.abs(minutes);
    if (minutes < 1) return ('less than a minute');
    if (minutes < 50) return (minutes + ' minute' + (minutes == 1 ? '' : 's'));
    if (minutes < 90) return ('about one hour');
    if (minutes < 1080) return (Math.round(minutes / 60) + ' hours');
    if (minutes < 1440) return ('one day');
    if (minutes < 2880) return ('about one day');
    else {
        days = Math.round(minutes / 1440);
        if (days < 31) return days + ' days';
        else return 'about ' + Math.round(days / 30) + ' months';
    }
}

function dli(x, a, b, c) {
    if (x == 1) return a;
    else {
        if (x % 10 > 1 && x % 10 < 5 && !(x % 100 >= 10 && x % 100 <= 21)) return x + " " + b;
        else return x + " " + c;
    }
}

function response_to(m_id, c_id, author) {
    $("#response_to_" + m_id).value = c_id;
    $("#response_to_label_" + m_id).html("Reply to user : " + author + "[<a onClick='clear_response_to(" + m_id + ", " + c_id + ")' style='cursor: pointer'>cancel<\/a>]");
}

function clear_response_to(m_id, c_id) {
    $("#response_to_" + m_id).attr("value") = "";
    $("#response_to_label_" + m_id).html("Comment:");
}

var BrowserDetect = {
    init: function () {
        this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
        this.version = this.searchVersion(navigator.userAgent)
            || this.searchVersion(navigator.appVersion)
            || "an unknown version";
        this.OS = this.searchString(this.dataOS) || "an unknown OS";
    },
    searchString: function (data) {
        for (var i = 0; i < data.length; i++) {
            var dataString = data[i].string;
            var dataProp = data[i].prop;
            this.versionSearchString = data[i].versionSearch || data[i].identity;
            if (dataString) {
                if (dataString.indexOf(data[i].subString) != -1)
                    return data[i].identity;
            }
            else if (dataProp)
                return data[i].identity;
        }
    },
    searchVersion: function (dataString) {
        var index = dataString.indexOf(this.versionSearchString);
        if (index == -1) return;
        return parseFloat(dataString.substring(index + this.versionSearchString.length + 1));
    },
    dataBrowser: [
        {
            string: navigator.userAgent,
            subString: "OmniWeb",
            versionSearch: "OmniWeb/",
            identity: "OmniWeb"
        },
        {
            string: navigator.vendor,
            subString: "Apple",
            identity: "Safari"
        },
        {
            prop: window.opera,
            identity: "Opera"
        },
        {
            string: navigator.vendor,
            subString: "iCab",
            identity: "iCab"
        },
        {
            string: navigator.vendor,
            subString: "KDE",
            identity: "Konqueror"
        },
        {
            string: navigator.userAgent,
            subString: "Firefox",
            identity: "Firefox"
        },
        {
            string: navigator.vendor,
            subString: "Camino",
            identity: "Camino"
        },
        {		// for newer Netscapes (6+)
            string: navigator.userAgent,
            subString: "Netscape",
            identity: "Netscape"
        },
        {
            string: navigator.userAgent,
            subString: "MSIE",
            identity: "IE",
            versionSearch: "MSIE"
        },
        {
            string: navigator.userAgent,
            subString: "Gecko",
            identity: "Mozilla",
            versionSearch: "rv"
        },
        { 		// for older Netscapes (4-)
            string: navigator.userAgent,
            subString: "Mozilla",
            identity: "Netscape",
            versionSearch: "Mozilla"
        }
    ],
    dataOS: [
        {
            string: navigator.platform,
            subString: "Win",
            identity: "Windows"
        },
        {
            string: navigator.platform,
            subString: "Mac",
            identity: "Mac"
        },
        {
            string: navigator.platform,
            subString: "Linux",
            identity: "Linux"
        }
    ]

};