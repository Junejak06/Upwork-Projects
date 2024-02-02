
// On Installed Script
chrome.runtime.onInstalled.addListener(function() {

    // Register a context menu action
    chrome.contextMenus.create({
        id: "aliexpressSearchByImage",
        title: "Search AliExpress By Image",
        contexts: [ "image" ],
        visible: true
    });

});

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    var imageUrl = info.srcUrl;

    // Check if this is an inline image
    if (imageUrl.indexOf('base64') > -1) {
        searchByInlineImage(imageUrl, redirectToAliseeksImageSearch);
    } else {
        redirectToAliseeksImageSearch({
            imageUrl: imageUrl
        });
    }
});

function redirectToAliseeksImageSearch(searchProperties) {
    var aliseeksUrl = environment.aliseeks.url + '/search/image';

    var appRefParam = 'aref=' + getAliseeksReferral();
    var appVersionParam = 'av=' + getManifestVersion();
    var imageQueryParam = '';

    if (searchProperties['imageUrl']) {
        imageQueryParam = 'imageurl=' + encodeURIComponent(searchProperties['imageUrl']);
    } else if (searchProperties['fileKey']) {
        imageQueryParam = 'fskey=' + searchProperties['fileKey'];
    }

    var queryParameters = [ appRefParam, appVersionParam, imageQueryParam ].join('&');

    var resolvedUrl = aliseeksUrl + '?' + queryParameters;

    chrome.tabs.create({ url: resolvedUrl });
}

function searchByInlineImage(imageUrl) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST",  environment.aliseeks.api + "/upload/image/inline", true);

    xhr.onload = function () {
        var uploadResponse = JSON.parse(xhr.responseText);
        if (xhr.readyState === 4 && xhr.status === 200) {
            redirectToAliseeksImageSearch({
                fileKey: uploadResponse.key
            });
        } else {
            console.error(uploadResponse);
        }
    };

    var data = {
        inlineImage: imageUrl
    };

    xhr.setRequestHeader("Content-Type", "application/json; charset=utf-8");
    xhr.send(JSON.stringify(data));
}
