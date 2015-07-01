var Engine = {

    init: function () {
        this.init_msg();
    },

    notify: function (msg) {
        n = $('#notify');
        n.text(msg);
        n.show();
        setTimeout("n.fadeOut(1000)", 3000);
    },

    // MSGing
    init_msg: function () {
        $('#status').keyup(function () {
            Engine.msg_box_counter($(this));
        });
    },

    msg_box_counter: function (t) {
        if (t.val().length > 140) $('#status_left').css('color', 'red');
        else $('#status_left').css('color', 'black');

        $('#status_left').html(140 - t.val().length);
    },

    msg_box_submit: function () {
        if ($('#status').val().length == 0 || $('#status').val().length > 140) return false;

        $.post($('#msg_form').attr('action'), {
            'ajax': 1,
            'text': $('#status').val()
        }, function (data, status) {
            if (status == 'success') {
                Engine.notify(data);
                Engine.msg_box_toggle();
                $('#status').val('');
            }
            else {
                Engine.notify(data);
            }
        });
    },

    msg_box_toggle: function (username) {
        if (username != undefined) {
            $('#msg_box').show();
            $('html, body').animate({scrollTop: 0}, 'slow');
        } else {
            $('#msg_box').toggle();
            return;
        }

        if ($.inArray('@' + username, $('#status').val().split(' ')) < 0)
            $('#status').val('@' + username + ' ' + $('#status').val());
        $('#status').val($('#status').val().trim());
        Engine.msg_box_counter($('#status'));
    },

    // Tabs

    tab_switch: function (name, url) {
        this.tab = $('#tab_' + name);
        this.indicator = $('#tab_' + name + '_indicator');

        $('.tab_selected').removeClass('tab_selected');

        if (this.tab.hasClass('tab_selected') == false) {
            this.tab.addClass('tab_selected');
        }
        this.indicator.show();
        this.tab_load(url);
    },

    tab_load: function (url) {
        $('#msgs').load(url + '?ajax=1');
        this.indicator.hide();
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

// C O U N T D O W N
var Timer = function () {
    return this;
}

Timer.timeUntil = function (delta) {
    // alert(delta);
    var hours = Math.floor(delta / 3600);
    var minutes = Math.floor(delta / 60);
    var seconds = Math.floor(((delta / 60) - minutes) * 60);
    if (seconds < 10) seconds = '0' + seconds;
    if (hours > 0)
        if (hours < 10) {
            if (minutes - (hours * 60) < 10) return hours + ':0' + (minutes - (hours * 60)) + ':' + seconds;
            else return hours + ':' + (minutes - (hours * 60)) + ':' + seconds;
        }
        else return hours + ':' + (minutes - (hours * 60)) + ':' + seconds;
    else
        return minutes + ':' + seconds;
}

Timer.prototype = {

    init: function (t) {
        field = t;

        till = new Date(Date.parse(field.get(0).innerHTML));
        delta = Math.floor((new Date() - till) / 1000);
        if (delta >= 0) {
            field.text('0');
            return;
        }

        field.text(Timer.timeUntil(Math.abs(delta)));
        ticker = setInterval(this.tick, 1000);
    },

    tick: function () {
        delta = Math.floor((new Date() - this.till) / 1000);
        if (delta >= 0) {
            // done
            window.location.reload();
            clearInterval(this.ticker);
        }

        this.field.text(Timer.timeUntil(Math.abs(delta)));
    },

    timeUntil: function (delta) {
        // alert(delta);
        var hours = Math.floor(delta / 3600);
        var minutes = Math.floor(delta / 60);
        var seconds = Math.floor(((delta / 60) - minutes) * 60);
        if (seconds < 10) seconds = '0' + seconds;
        if (hours > 0)
            if (hours < 10) {
                if (minutes - (hours * 60) < 10) return hours + ':0' + (minutes - (hours * 60)) + ':' + seconds;
                else return hours + ':' + (minutes - (hours * 60)) + ':' + seconds;
            }
            else return hours + ':' + (minutes - (hours * 60)) + ':' + seconds;
        else
            return minutes + ':' + seconds;
    }
}