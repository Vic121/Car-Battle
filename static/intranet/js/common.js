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
            return 'in ' + distance;
        }
        else {
            return distance + ' ago';
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

this.imagePreview = function () {
    /* CONFIG */

    xOffset = 10;
    yOffset = 30;

    // these 2 variable determine popup's distance from the cursor
    // you might want to adjust to get the right result

    /* END CONFIG */
    $("a.preview").hover(function (e) {
            this.t = this.title;
            this.title = "";
            var c = (this.t != "") ? "<br/>" + this.t : "";
            $("body").append("<p id='preview'><img src='" + this.href + "' alt='Image preview' />" + c + "</p>");
            $("#preview")
                .css("top", (e.pageY - xOffset) + "px")
                .css("left", (e.pageX + yOffset) + "px")
                .fadeIn("fast");
        },
        function () {
            this.title = this.t;
            $("#preview").remove();
        });
    $("a.preview").mousemove(function (e) {
        $("#preview")
            .css("top", (e.pageY - xOffset) + "px")
            .css("left", (e.pageX + yOffset) + "px");
    });
};