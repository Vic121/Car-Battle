FB.init({appId: 225960433127, status: true, cookie: true, xfbml: true});
FB.Event.subscribe('auth.sessionChange', function (response) {
    if (response.session) {
        document.location = 'http://www.car-battle.com/'
    } else {
        // out
    }
});

//stream publish method
function streamPublish(name, description, hrefTitle, hrefLink, userPrompt) {
    FB.ui({
            method: 'stream.publish',
            message: '',
            attachment: {
                name: name,
                caption: '',
                description: (description),
                href: hrefLink
            },
            action_links: [
                {text: hrefTitle, href: hrefLink}
            ],
            user_prompt_message: userPrompt
        },
        function (response) {

        });
}

function showStream() {
    FB.api('/me', function (response) {
        //console.log(response.id);
        streamPublish(response.name, 'Car Battle contains geeky stuff', 'hrefTitle', 'http://car-battle.com', "Share car-battle.com");
    });
}

function share() {
    var share = {
        method: 'stream.share',
        u: 'http://car-battle.com/'
    };

    FB.ui(share, function (response) {
        console.log(response);
    });
}

function graphStreamPublish() {
    var body = 'Reading New Graph api & Javascript Base FBConnect Tutorial';
    FB.api('/me/feed', 'post', {message: body}, function (response) {
        if (!response || response.error) {
            alert('Error occured');
        } else {
            alert('Post ID: ' + response.id);
        }
    });
}

function fqlQuery() {
    FB.api('/me', function (response) {
        var query = FB.Data.query('select name, hometown_location, sex, pic_square from user where uid={0}', response.id);
        query.wait(function (rows) {

            document.getElementById('name').innerHTML =
                'Your name: ' + rows[0].name + "<br />" +
                '<img src="' + rows[0].pic_square + '" alt="" />' + "<br />";
        });
    });
}

function setStatus() {
    status1 = document.getElementById('status').value;
    FB.api(
        {
            method: 'status.set',
            status: status1
        },
        function (response) {
            if (response == 0) {
                alert('Your facebook status not updated. Give Status Update Permission.');
            }
            else {
                alert('Your facebook status updated');
            }
        }
    );
}