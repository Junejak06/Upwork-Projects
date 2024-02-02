var page_title=document.title;
var page_url=location.href;



setInterval(function() {
	
$("img").each(function() {
        $(this).attr('oncontextmenu',"return true;");
		$(this).attr('onmousedown',"return true;");
		$(this).attr('onmouseup',"return true;");
		$(this).attr('onselectstart',"return true;");
    });
	
if(document.addEventListener)
{document.addEventListener('contextmenu', function(e) { e.stopPropagation(); }, true);}
else {if(document.attachEvent){
document.attachEvent('oncontextmenu', function() { event.cancelBubble = false; });}}
	

 
}, 1000);


//aliexpress allow mouse right click
if(page_url.indexOf("aliexpress"))
{
//alert(page_url);
var script = document.createElement("script");
script.type = "text/javascript";
script.innerHTML = "\n" +
	"setInterval(function() {\n"+
    "document.oncontextmenu = null;\n" +
    "document.onselectstart = null;\n" +
    "document.onmousedown = null;\n" +
    "document.onclick = null;\n" +
    "document.oncopy = null;\n" +
    "document.oncut = null;\n" +
    "var elements = document.getElementsByTagName('*');\n" +
    "for (var i = 0; i < elements.length; i++) {\n" +
    "    elements[i].oncontextmenu = null;\n" +
    "    elements[i].onselectstart = null;\n" +
    "    elements[i].onmousedown = null;\n" +
    "    elements[i].oncopy = null;\n" +
    "    elements[i].oncut = null;\n" +
    "}\n"+
	"}, 1000);\n";
var style = document.createElement("style")
style.innerHTML = "\n" +
    "* {\n" +
    "    -webkit-user-select: auto !important;\n" +
    "}";
window.onload = document.body.appendChild(script);
window.onload = document.body.appendChild(style);

}


//search similar items link
if(document.getElementsByClassName('product-title').length>0 && document.getElementById('search_similar')==null)
{	
//search product id	
var cur_meta_ogurl2=$("meta[property='og:url']").attr("content");
var tmp_p_id2=cur_meta_ogurl2.split('/item/')[1];	
var cur_product_id=tmp_p_id2.split('.html')[0];	



var similar_button='<div id="search_similar" style="padding-top:4px;"><img  src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAADVElEQVQ4jW2Ty29UZRjGn+825za3M9PO1FagpTMtcGbKoqDY6dKYaBAiuGqjGxcGTYjExI1/A0itCJiQmBBN1EQXIrWBTa00uEDTsY0MovZmFdvOpdOZM52e73wupEAiT/Ju3rzPL+/ieYhSCts6d/7CS77nveZLL0cpDflSlinj35GAdt6X8vrJN088PL4vopTCxUsfG8169RNdN54NJp/8i4XsChj3me8xr7IWXftzvqNULF4WhnnynbdPbf4PMDo6+lXIjg+IjtRciQXllmnLgKapIAOiaBDTLYnfbk31TP9460vKxevnPhiV2wDWmki+rGnaKaNr391/jIRXjXU2PSPs04ChqGYozQz6LbG4l+rcVVxZmntuaurGzWvXrv9x/PgxAACVW803Qk/sWF7XbK9u72iCCZgUsDhgMYCDwPUZtHB8a3//U0vJROLE8vKy2P6AQqlDIhyr0FibB8JgUfXAbFHAYiA6BQWhbHe6txyLxQ5tbjb0oaEhAgCcMcYDpiU13fDNrYfmIAUiAsIW0CwGbjAoEY1AShnL5XLhzUajBkByKeWWpQnicaCpAPO+2RYQbToidgARTghRUG65WJFSylI0GhWVSoX+B/D9KX+92NGa7Gz4oGAAQhysVUMwoaPVYMRs+qhLH9WZ/LTlNho/FAqFDUqpBwB8YXHpw2Do58uD3XtWNT0ka5LAYmBhDlNQIqRC0/NV2d1Yd8e/ubI7n89fsm17Y3JyUgEAy2b7fl2593cfk82De9Pda6EAVxYnwuQwGIGSCpV6rVq78P57e6GUbgZD6WQiOXH06JGVB0EaGMiFe9Kpi46TOXLgmdxid7qnFo1GAuViUeSnf9LHrnzdRkC0wy8eBqUUExPfu7Va7a2zZ09/RLa70NXVpRu6/nw2m301Ho8/7Xme7XlesVyp3JiZmfm0v//gu5nMvgP7+/qwc+cufPb5F161WnXIo2VyHIe7rmsMDg5GMplMZHV1tTk+Pl4ulUp1x8nYqVR6sr29rTOZSECIAE6fOTNMHy3G7Oys5zjORktLy71UKjXX3t6+lM1k1hYWFmpjY1eX3Hr9hfn5xd9/uV3A1bFv7965U7gJpdRjZ2RkhDxuPzz8itbbu6efc5HgnAf/Ba9tg9l3IwDnAAAAAElFTkSuQmCC\" style="padding-right:5px;padding-left:2px;"/>'+
' <a href="http://my.aliexpress.com/wishlist/wish_item_similar_product_list.htm?productId='+cur_product_id+'" id="search_similar_link" target="_blank">'+chrome.i18n.getMessage('search_similar')+'</a></div>';
if($('.product-action').length > 0){$('.product-action').after(similar_button);}

$("#search_similar_link").attr('onclick','return false;');
var similar_link='http://alipromo.com/redirect/cpa/o/ee377225bbcd6161fd5f61e9398fcba4?sub=aliexpress_search_by_image&to='+$("#search_similar_link").attr('href');
$("#search_similar_link").click(function() {chrome.runtime.sendMessage({"search_similar": similar_link}, function(response) {});});
} 