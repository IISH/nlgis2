var args = require('system').args,
    page = require('webpage').create(),
    url = args[1];

page.onConsoleMessage = function (msg) {
    console.log(msg);
};

page.onLoadFinished = function() {
    page.evaluate(function() {
        console.log(document.documentElement.outerHTML);
    });
    phantom.exit();
};

page.open(url);
