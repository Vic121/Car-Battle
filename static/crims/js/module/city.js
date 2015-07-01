var update_hint = function (that, price, speed) {
    var id = that.id;
    var cost_id = id.replace('build_', 'cost_');
    var time_id = id.replace('build_', 'time_');
    var units = $('#' + id).attr('value');

    $('#' + cost_id + '> b').text('$' + price * units);
    $('#' + time_id + '> b').text(Timer.timeUntil(speed * units));
};