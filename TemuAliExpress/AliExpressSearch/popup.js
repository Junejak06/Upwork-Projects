function searchbyimage(url)
{
	
		var sbi_image = url;
		
		//var google_url="";
		//if(chrome.i18n.getMessage("lang")=="ru"){google_url="https://www.google.ru/searchbyimage?hl=ru&site=imghp&q=site:ru.aliexpress.com&authuser=0&image_url=";}
		//else{google_url="https://www.google.com/searchbyimage?hl=en&site=imghp&q=site:aliexpress.com&authuser=0&image_url=";}
		//var sbi_url =  google_url+ sbi_image;
		
		 var sbi_url = 'https://www.aliseeks.com/search/image?aref=ff-sbi&imageurl=' + encodeURIComponent(sbi_image);
		
		
		
		if (sbi_image == "" || sbi_image == null)return;
		
		
chrome.tabs.create({"url": sbi_url});
		
}



//onsearch submit
$("#search_submit").click(function(){
var cur_search = document.getElementById("search").value.replace(/\s/,'%2520');
//chrome.tabs.create({ url: 'http://www.aliexpress.com/wholesale?SearchText='+encodeURIComponent(cur_search) })
if(cur_search.indexOf("http://")==0 || cur_search.indexOf("https://")==0)
{	
searchbyimage(cur_search);
}else{
if(chrome.i18n.getMessage('lang')!='ru')
{chrome.tabs.create({ url: 'http://alipromo.com/redirect/cpa/o/ee377225bbcd6161fd5f61e9398fcba4?sub=aliexpress_search_by_image&to=http%3A%2F%2Fwww.aliexpress.com%2Fwholesale%3FSearchText%3D'+encodeURIComponent(cur_search+'&SortType=total_tranpro_desc') });}
else{chrome.tabs.create({ url: 'http://alipromo.com/redirect/cpa/o/ee377225bbcd6161fd5f61e9398fcba4?sub=aliexpress_search_by_image&to=http%3A%2F%2Fru.aliexpress.com%2Fwholesale%3FSearchText%3D'+encodeURIComponent(cur_search+'&SortType=total_tranpro_desc') });}

}	

});

//onsearch click 
$("#search").click(function(){$("#search").val("");});


//onlogo click 
$("#aliexpress").click(function(){
	
if(chrome.i18n.getMessage('lang')!='ru')
{chrome.tabs.create({ url: 'http://alipromo.com/redirect/cpa/o/ee377225bbcd6161fd5f61e9398fcba4?sub=aliexpress_search_by_image&to=http%3A%2F%2Fwww.aliexpress.com' });}
else{chrome.tabs.create({ url: 'http://alipromo.com/redirect/cpa/o/ee377225bbcd6161fd5f61e9398fcba4?sub=aliexpress_search_by_image&to=http%3A%2F%2Fru.aliexpress.com' });}
	
	
});

$('[inp]').each(function() {
  var el = $(this);
  var resourceName = el.attr('inp');
  var resourceText = chrome.i18n.getMessage(resourceName);
  el.val(resourceText);
});
