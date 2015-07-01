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

        if (delta_minutes < 0) {
            return 'za ' + distance;
        }
        else {
            return distance + ' temu';
        }
        // return distance + ((delta_minutes < 0) ? ' from now' : ' ago')
    } else {
        // return 'on ' + system_date.toLocaleDateString();
        return false;
    }
}

function distance_of_time_in_words(minutes) {
    if (minutes.isNaN) return "";
    minutes = Math.abs(minutes);
    if (minutes < 1) return ('mniej niż minutę');
    if (minutes < 50) return (minutes + ' minut' + (minutes == 1 ? 'ę' : '') + (minutes > 1 && minutes < 5 ? 'y' : ''));
    if (minutes < 90) return ('około godzinę');
    if (minutes < 1080) return (Math.round(minutes / 60) + ' godzin' + (Math.round(minutes / 60) > 1 && Math.round(minutes / 60) < 5 ? 'y' : ''));
    if (minutes < 1440) return ('jeden dzień');
    if (minutes < 2880) return ('około jeden dzień');
    else {
        days = Math.round(minutes / 1440);
        if (days < 31) return days + ' dni';
        if (Math.round(days / 30) == 1) return 'około ' + Math.round(days / 30) + ' miesiąc';
        else return 'około ' + Math.round(days / 30) + ((Math.round(days / 30) > 1 && Math.round(days / 30) < 5) ? ' miesiące' : ' miesięcy')
    }
}