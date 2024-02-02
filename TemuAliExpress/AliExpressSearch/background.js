function searchbyimage(info)
{
	
		//var sbi_image = info.srcUrl;
		
		//var google_url="";
		//if(chrome.i18n.getMessage("lang")=="ru"){google_url="https://www.google.ru/searchbyimage?hl=ru&site=imghp&q=site:aliexpress.com&authuser=0&image_url=";}
		//else{google_url="https://www.google.com/searchbyimage?hl=en&site=imghp&q=site:aliexpress.com&authuser=0&image_url=";}
		//var sbi_url =  google_url+ sbi_image;
		
		//var sbi_url = 'https://www.aliseeks.com/search/image?aref=ff-sbi&imageurl=' + encodeURIComponent(sbi_image);
		
		
		//if (sbi_image == "" || sbi_image == null)return;
		
		
//chrome.tabs.create( {"url": sbi_url});
//////////////////////////////////////////////////////////////
var imageUrl = info.srcUrl;
// Check if this is an inline image
    if (imageUrl.indexOf('base64') > -1) {
        searchByInlineImage(imageUrl, redirectToAliseeksImageSearch);
    } else {
        redirectToAliseeksImageSearch({
            imageUrl: imageUrl
        });
    }
//////////////////////////////////////////////////////////////	
}


function redirectToAliseeksImageSearch(searchProperties) {
    var aliseeksUrl =  'https://www.aliseeks.com/search/image';

    var appRefParam = 'aref=ff-sbi';
    var siteParam = 'site=ali';
    var imageQueryParam = '';

    if (searchProperties['imageUrl']) {
        imageQueryParam = 'imageurl=' + encodeURIComponent(searchProperties['imageUrl']);
    } else if (searchProperties['fileKey']) {
        imageQueryParam = 'fskey=' + searchProperties['fileKey'];
    }

    var queryParameters = [ appRefParam, siteParam, imageQueryParam ].join('&');

    var resolvedUrl = aliseeksUrl + '?' + queryParameters;
    
    chrome.tabs.create({ url: resolvedUrl });
}

function searchByInlineImage(imageUrl) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST",  "https://api.aliseeks.com/upload/image/inline", true);

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




chrome.contextMenus.create({
	"title" : chrome.i18n.getMessage("menu_name"),
	"type" : "normal",
	"contexts" : ["image"],
	"onclick" : searchbyimage
});



chrome.runtime.onMessage.addListener(function(message,sender,sendResponse){
  if(message.search_similar!="")
  {chrome.tabs.create( {"url": message.search_similar}, function(tab){});}
  
});