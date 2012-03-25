####################################################################################################
# TODO:
# 	- Implement support for ScrewAttack?
#	- Implement support for Retrospectives?
#	- Other shows?
####################################################################################################

import re

####################################################################################################

GT_PREFIX                   = '/video/gametrailers'
GT_PLAY_PREFIX              = '/video/gametrailers-play'

RSS_URL = "http://www.gametrailers.com/gt%s_podcast.xml"
DETAIL_URL = "http://www.gametrailers.com/neo/?page=xml.mediaplayer.Mrss&mgid=mgid:moses:video:gametrailers.com:%s&keyvalues={keyvalues}"
FEATURES_URL = "http://feeds.gametrailers.com/rssgenerate.php?s1=&favplats[xb360]=xb360&favplats[ps3]=ps3&favplats[pc]=pc&type[feature]=on&quality[hd]=on&orderby=newest&limit=20"
CHANNEL_URL = "http://feeds.gametrailers.com/rssgenerate.php?game1id=%s&vidformat[mp4]=on&quality[hd]=on&orderby=newest&limit=20"

CHANNELS = [
	    {"title" : "Anthology",	"url" : "11170"},
	    {"title" : "CountDown",	"url" : "2111"},
	    {"title" : "EpicBattleCry",	"url" : "10944"},
	    {"title" : "GTTV",		"url" : "6426"},
	    {"title" : "CountDown",	"url" : "2111"},
	    {"title" : "Top 100", 	"url" : "15268"},
	    {"title" : "Hey Ash Watcha Playin",	"url" : "11350"},
	    {"title" : "Pach Attack", 	"url" : "12619"},
	    {"title" : "Pop Fiction", 	"url" : "13123"},
	    {"title" : "Science of Games",	"url" : "13798"}
]

CATEGORIES = [
	    {"title" : "Reviews",	"rss" : "rev"},
	    {"title" : "Previews",	"rss" : "prev"},
	    {"title" : "Interviews",	"rss" : "int"}
]

PLATFORMS = [
	    {"title" : "PS3",		"rss" : "ps3"},
	    {"title" : "XBox360",	"rss" : "360"},
	    {"title" : "Wii",		"rss" : "wii"},
	    {"title" : "PSP",		"rss" : "psp"},
	    {"title" : "Nintendo DS",	"rss" : "ds"}
]

OTHER_PLATFORMS = ['pc', 'xbox', 'gc', 'ps2', 'gba', 'ds', 'psp', 'mob' ] ### Currently not implemented

MAX_ITEM_COUNT          = 20 # Maximum number of items to display per page

DEBUG_XML_RESPONSE		     = False
CACHE_INTERVAL                       = 1800 # Since we are not pre-fetching content this cache time seems reasonable 
CACHE_RSS_INTERVAL                   = 1800
CACHE_HIGHLIGHTS_INTERVAL            = 1800
CACHE_SEARCH_INTERVAL		     = 600

NAMESPACES = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd','exInfo':'http://www.gametrailers.com/rssexplained.php', 'media':'http://search.yahoo.com/mrss/'}

LOGIN_PREF_KEY = "login"
PASSWD_PREF_KEY = "passwd"
LOGGED_IN = "loggedIn"

ART = 'art-default.png'
ICON = 'icon-default.png'

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(GT_PREFIX, MainMenu, L('gt'), ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')
  ObjectContainer.art = R(ART)
  ObjectContainer.view_group = 'List'
  ObjectContainer.title1 = L('gt')
  DirectoryObject.thumb = R(ICON)
  HTTP.CacheTime = CACHE_INTERVAL

def ValidatePrefs():
  userName = Prefs['LOGIN_PREF_KEY']
  password = Prefs['PASSWD_PREF_KEY']
  Dict['LOGGED_IN'] = False
  if (userName != None) and (password != None):
    values = {} 
    values['action']='userLogin'
    values['username']=userName
    values['password']=password
    Log("Login")
    response = HTTP.Request("http://www.gametrailers.com/quick_register_ajaxfuncs.php", values=values, cacheTime=0).content
    if(response == None or len(response.strip()) == 0):
      Log("Secondary login")
      response = HTTP.Request('http://www.gametrailers.com/includes/cookie_proc_ajax.php', values=values, cacheTime=0).content
      Dict['LOGGED_IN'] = True

def MainMenu():

  oc = ObjectContainer(no_cache=True)
  
  oc.add(DirectoryObject(key=Callback(Custom_RSS_Browser, feed={"title":"Features", "url":FEATURES_URL}), title="Features"))
  oc.add(DirectoryObject(key=Callback(CategoryBrowser, genre="Platforms"), title="Platforms"))
  oc.add(DirectoryObject(key=Callback(CategoryBrowser, genre="Categories"), title="Categories"))
  oc.add(DirectoryObject(key=Callback(ChannelsMenu), title="Channels"))
  
  return oc

def ChannelsMenu():
  oc = ObjectContainer(title2="Channels", no_cache=True)
  
  oc.add(DirectoryObject(key=Callback(FeedBrowser, rss_feed={'title':'Bonus Round', 'rss':'bonusround'}), title="Bonus Round"))
  oc.add(DirectoryObject(key=Callback(FeedBrowser, rss_feed={'title':'Invisible Walls', 'rss':'iw'}), title="Invisible Walls"))
  for channel in CHANNELS:
    oc.add(DirectoryObject(key=Callback(Custom_RSS_Browser, feed=channel), title=channel['title']))
  
  return oc

def CategoryBrowser(genre):
  oc = ObjectContainer(title2=genre, no_cache=True)
  
  if genre == 'Platforms':
    for platform in PLATFORMS:
      oc.add(DirectoryObject(key=Callback(FeedBrowser, rss_feed=platform), title=platform['title']))
  elif genre == 'Categories':
    for category in CATEGORIES:
      oc.add(DirectoryObject(key=Callback(FeedBrowser, rss_feed=category), title=category['title']))
  else:
    pass
  
  return oc

def FeedBrowser(rss_feed):
  oc = ObjectContainer(title2=rss_feed['title'], no_cache=True)
  
  feed = RSS.FeedFromURL(RSS_URL % rss_feed['rss'])
  feed_thumb = feed.feed.image.href

  for item in feed.entries:
    title = item.title
    tagline = item.subtitle
    summary = item.summary
    url = item.enclosures[0].href
    duration = int(item.itunes_duration)*1000
    pubDate = Datetime.ParseDate(item.updated).date()
    page_url = item.id
    
    oc.add(VideoClipObject(url=url, title=title, tagline=tagline, summary=summary, duration=duration, originally_available_at=pubDate, thumb=Callback(Thumb, url=page_url, fallback=feed_thumb)))
    
  return oc

def Custom_RSS_Browser(feed):
  oc = ObjectContainer(title2=feed['title'], no_cache=True)
  if not 'http://' in feed['url']:
    feed_url = CHANNEL_URL % feed['url']
  else:
    feed_url = feed['url']
  content = HTTP.Request(feed_url).content.replace('exInfo:', '')
  data = XML.ElementFromString(content)
  for item in data.xpath('//item'):
    title = item.xpath('.//title')[0].text
    summary = String.StripTags(item.xpath('.//description')[0].text)
    date = Datetime.ParseDate(item.xpath('.//pubDate')[0].text).date()
    thumb = item.xpath('.//image')[0].text
    page_url = item.xpath('./link')[0].text
    
    oc.add(VideoClipObject(url=page_url, title=title, summary=summary, originally_available_at=date, thumb=Callback(Thumb, url=None, fallback=thumb)))
    
  return oc

def Thumb(url, fallback):
  try:
    try:
      video_id = re.search(': (d+)$', url).group(1)
      feed = RSS.FeedFromURL(DETAIL_URL % video_id)
    except:
      video_id = url.split('/')[-1]
      feed = RSS.FeedFromURL(DETAIL_URL % video_id)
    
    thumb_url = feed.entries[0].media_thumbnail[0]['url']
    data = HTTP.Request(thumb_url, cacheTime=0).content
    return DataObject(data, 'image/jpeg')
  except:
    if fallback == R(ICON):
      return Redirect(R(ICON))
    else:
      try:
	data = HTTP.Request(fallback, cacheTime=CACHE_1MONTH).content
	return DataObject(data, 'image/jpeg')
      except:
	return Redirect(R(ICON))