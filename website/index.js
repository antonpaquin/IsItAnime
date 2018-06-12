var e_upload_url = document.getElementById('upload-url');
var e_message = document.getElementById('message');
var e_submessage = document.getElementById('submessage');
var e_upload_file = document.getElementById('upload-file');
var e_preview = document.getElementById('preview');
var e_reclass = document.getElementById('div-reclass');
var e_reclass_msg = document.getElementById('reclass-msg');
var e_reclass_anime = document.getElementById('reclass-anime');
var e_reclass_notanime = document.getElementById('reclass-notanime');
var recent_key;

e_upload_url.onclick = function() {
    e_upload_url.placeholder = '';
    e_upload_url.value = '';
}
e_upload_url.onblur = function() {
    e_upload_url.placeholder = 'Upload URL';
    if (e_upload_url.value !== '') {
        classify_url(e_upload_url.value);
    }
}
e_upload_url.onkeydown = function(event) {
    if (event.keyCode == 13) {
        classify_url(e_upload_url.value);
        e_upload_url.blur();
    }
}
e_upload_file.onchange = function() {
    if (e_upload_file.files && e_upload_file.files[0]) {
        set_message('Uploading...');

        var reader_preview = new FileReader();
        reader_preview.onload = function(e) {
            e_preview.src = e.target.result;
            classify_file(e.target.result.split(',')[1]);
        }
        reader_preview.readAsDataURL(e_upload_file.files[0]);
    }
}

function set_message(msg) {
    e_message.innerHTML = msg;
    e_message.style.opacity = 1;
}

function set_submessage(msg) {
    e_submessage.innerHTML = msg;
    e_submessage.style.opacity = 1;
}

function encode_url(base, params) {
    let res = [];
    for (let p in params) {
        res.push(encodeURIComponent(p) + '=' + encodeURIComponent(params[p]));
    }
    return base + '?' + res.join('&');
}

function classify_url(url) {
    set_message('Uploading...');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', encode_url('https://api.isitanime.website/isitanime', {'url': url}));
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('daijoubu desu~!');
            handle_response_url(xhr.response);
        } else {
            set_message('Error');
        }
    };
    xhr.setRequestHeader('accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'image/something');
    xhr.send();
    set_message('Classifying...');
}

function handle_response_url(response) {
    data = JSON.parse(response);
    if ('error' in data) {
        set_message('Error: ' + data['error']);
        return;
    }
	e_preview.src = 'data:image/jpeg;base64,' + data['data'];
    display_classification(data);
}

function display_classification(data) {
    anime_percent = Math.round(1000 * data.classes.anime) / 10;
    set_message(anime_percent + '% Anime');

    if (anime_percent > 99) {
        e_submessage.style.fontFamily = 'irohamaru';
    } else {
        e_submessage.style.fontFamily = 'cantarell';
    }

    if (anime_percent > 99) {
        set_submessage('~~アニメです~~');
    } else if (anime_percent > 85) {
        set_submessage('This is anime!');
    } else if (anime_percent > 60) {
        set_submessage('This is somewhat anime');
    } else if (anime_percent > 40) {
        set_submessage('This might be anime');
    } else if (anime_percent > 15) {
        set_submessage('Probably not anime');
    } else {
        set_submessage('This is not anime');
    }
    recent_key = data.key;
    expose_reclassify();
}

function classify_file(file_data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://api.isitanime.website/isitanime');
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('daijoubu desu~!');
            handle_response_file(xhr.response);
        } else {
            set_message('Error');
        }
    };
    xhr.setRequestHeader('accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'image/something');
    xhr.send(file_data);
    set_message('Classifying...');
}

function handle_response_file(response) {
    data = JSON.parse(response);
    if ('error' in data) {
        set_message('Error: ' + data['error']);
        return;
    }
    display_classification(data);
}

function expose_reclassify() {
    e_reclass.style.opacity = 1;
    e_reclass.style.display = 'block';
    e_reclass_anime.style.display = 'block';
    e_reclass_notanime.style.display = 'block';
    e_reclass_msg.innerHTML = 'Help me get smarter?';
}

function hide_reclassify() {
    e_reclass_anime.style.display = 'none';
    e_reclass_notanime.style.display = 'none';
    e_reclass_msg.innerHTML = 'Thanks!';
}

function reclassify_http(clss) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', encode_url('https://api.isitanime.website/isitanime', {'classify': clss, 'key': recent_key}));
    xhr.onload = function() {
        if (xhr.status === 200) {
            console.log('daijoubu desu~!');
        } else {
            console.log('reclass failed');
        }
    };
    xhr.setRequestHeader('accept', 'application/json');
    xhr.send();
    hide_reclassify();
}

e_reclass_anime.onclick = function() {
    reclassify_http('anime');
}

e_reclass_notanime.onclick = function() {
    reclassify_http('notanime');
}
