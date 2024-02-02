
function getManifestVersion() {
    return getManifest().version;
}

function getAliseeksReferral() {
    return getManifest().referral;
}

function getManifest() {
    if(typeof ( chrome.runtime.getManifest ) == 'function') {
        return chrome.runtime.getManifest();
    }

    return {};
}
