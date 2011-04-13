import re

from ScrewAttack import *
from InvisibleWalls import *
from Countdown import *
from Retrospectives import *
from Anthology import *
from GTTV import *
from BonusRound import *

from Support import *

####################################################################################################

GT_PREFIX                   = '/video/gametrailers'
GT_PLAY_PREFIX              = '/video/gametrailers-play'

GT_URL                      = 'http://www.gametrailers.com'
GT_RSS_BASE                 = 'http://www.gametrailers.com/rssgenerate.php?s1='
GT_SEARCH_URL               = 'http://www.gametrailers.com/search.php?page=0&s=%s&str_type=movies&ac=1'
GT_SEARCH_BASE              = 'http://www.gametrailers.com/search.php'
GT_HIGHLIGHTS_URL           = 'http://www.gametrailers.com/index_ajaxfuncs.php?do=get_movie_page&type=%s&page=%d&loading=0'
GT_TOP20_URL                = 'http://www.gametrailers.com/top20.php?toplist=media&topsublist=%s&plattyfilt=all&page=%d'

GT_CATEGORIES               = [ 'allcategories', 'review', 'preview', 'interview', 'gameplay', 'trailer', 'feature' ]
# Available platforms. Note: There is a 'classic' platform RSS feed but there is no content in it
GT_PLATFORMS                = [ 'allplatforms', 'wii', 'xb360', 'ps3', 'pc', 'xbox', 'gc', 'ps2', 'gba', 'ds', 'psp', 'mob' ]

# Downloadable files are available in these formats
GT_MEDIATYPES               = [ 'mov', 'wmv', 'mp4' ]

MAX_ITEM_COUNT          = 20 # Maximum number of items to display per page

DEBUG_XML_RESPONSE		     = True
CACHE_INTERVAL                       = 1800 # Since we are not pre-fetching content this cache time seems reasonable 
CACHE_RSS_INTERVAL                   = 1800
CACHE_HIGHLIGHTS_INTERVAL            = 1800
CACHE_SEARCH_INTERVAL		     = 600

RSS_NAMESPACE                      = {'exInfo':'http://www.gametrailers.com/rssexplained.php'}

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
  MediaContainer.content = 'Items'
  MediaContainer.art = R(ART)
  MediaContainer.viewGroup = 'List'
  MediaContainer.title1 = L('gt')
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

  dir = MediaContainer(noCache=True)
  
  if (Dict['LOGGED_IN']):
  
      dir.Append(Function(DirectoryItem(HighlightsBrowser, title=L('highlights'), thumb=R(ICON))))
      dir.Append(Function(DirectoryItem(CategoryBrowser, title=L('categories'), thumb=R(ICON))))
      dir.Append(Function(DirectoryItem(ChannelBrowser, title=L('channels'), thumb=R(ICON))))
      dir.Append(Function(InputDirectoryItem(Search, title=L('search'), prompt=L('searchprompt'), thumb=R('search.png'))))
  dir.Append(PrefsItem(L('preferences'), thumb=R('icon-prefs.png')))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def ChannelBrowser(sender):

  dir = MediaContainer(title2 = L('channels'))

  # Some channels are only availalbe in SD, if the user has requested HD only then warn them
  sdwarn = ''
  if Prefs['quality-key'] == 'HD Only':
    sdwarn = " (SD Only)"

  # Ordering matches that on the site
  dir.Append(Function(DirectoryItem(GTTV, title=L('gttv'), thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(BonusRound, title=L('bonusround'), thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(InvisibleWalls, title=L('invisiblewalls') + sdwarn, thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(Retrospectives, title=L('retrospectives') + sdwarn, thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(Anthology, title=L('anthology'), thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(ScrewAttack, title=L('screwattack') + sdwarn, thumb=R(ICON))))
  dir.Append(Function(DirectoryItem(Countdown, title=L('countdown'), thumb=R(ICON))))


  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir



def CategoryBrowser(sender):

  dir = MediaContainer(title2 = L('categories'))

  for category in GT_CATEGORIES:
    dir.Append(Function(DirectoryItem(PlatformBrowser, title=L(category), thumb=R(ICON)), category=category))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def PlatformBrowser(sender, category):

  # First check to see if the user has selected a specific console as a preference
  platformKey = Prefs['platform-key']

  if platformKey != 'noselection':

    # User has selected a platform so select that automatically

    return RSSBrowser(sender=None, category=category, platform=platformKey)

  else:

    dir = MediaContainer(title1 = L('categories'), title2 = L(category))

    for platform in GT_PLATFORMS:
      dir.Append(Function(DirectoryItem(RSSBrowser, title=L(platform), thumb=R(ICON)), category=category, platform=platform))

    if DEBUG_XML_RESPONSE:
      Log(dir.Content())
    return dir

def RSSBrowser(sender, category, platform, offset=0, page=1):

  # Browse the 'customizable rss feeds'

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup='Details')
  if page > 1:
    dir.title1 = L(platform)
    dir.title2 = L('page') + ' ' + str(page)
  else:
    dir.title1 = L(category)
    dir.title2 = L(platform)

  rssUrl = GT_RSS_BASE

  if platform != 'allplatforms':
    rssUrl += '&favplats%5B' + platform + '%5D=' + platform


  if category != 'allcategories':
    rssUrl += '&type%5B' + category + '%5D=on'

  if Prefs['quality-key'] == 'HD Only':
    rssUrl += '&quality%5B%5D=on'
  elif Prefs['quality-key'] == 'SD Only':
    rssUrl += '&quality%5Bsd%5D=on'
  else:
    rssUrl += '&quality%5Beither%5D=on'

  rssUrl += "orderby=newest&limit=100"

  rssFeed = XML.ElementFromURL(rssUrl, cacheTime=CACHE_RSS_INTERVAL, errors='ignore')

  items = rssFeed.xpath('//channel/item')

  itemTotalCount = len(items)

  if itemTotalCount <= offset:
    return (MessageContainer(header=L('search'), message=L('nonefound'), title1=L('gt')))

  else:

    count = 0
    displayed = 0

    for item in items:

      # Skip until we reach 'offset'
      if count < offset:
        count += 1
        continue

      # Display at most MAX_ITEM_COUNT 
      if displayed >= MAX_ITEM_COUNT:
        break

      title = str(item.xpath("./title/text()")[0])

      if title == 'No Results Found - Back to Custom RSS Form':
        return (MessageContainer(header=L('rssfeed'), message=L('noitems'), title1=L('gt')))

      pageUrl = str(item.xpath("./exInfo:fileType/link/text()", namespaces=RSS_NAMESPACE)[0])
      thumb = item.xpath("./exInfo:image/text()", namespaces=RSS_NAMESPACE)[0]
      try:
	description = item.xpath("./description/text()")[0]
      except:
      	Log('No description for ' + title)
      	description = ''
      date = str(item.xpath("./pubDate/text()")[0])

      dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=pageUrl))
      count += 1
      displayed += 1

  if count < itemTotalCount:

    dir.Append(Function(DirectoryItem(RSSBrowser, title=L('nextpage'), summary='', subtitle='', thumb=R(ICON)), category=category, platform=platform, offset=count+1, page=page+1))


  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def HighlightsBrowser(sender):

  # List available 'highlights' sections

  dir = MediaContainer(title2 = L('highlights'))

  dir.Append(Function(DirectoryItem(HighlightsSectionBrowser, title=L('newest'), thumb=R(ICON)), section='newest'))
  dir.Append(Function(DirectoryItem(HighlightsSectionBrowser, title=L('featured'), thumb=R(ICON)), section='featured'))
  dir.Append(Function(DirectoryItem(HighlightsSectionBrowser, title=L('popular'), thumb=R(ICON)), section='popular'))
  dir.Append(Function(DirectoryItem(Top20Browser, title=L('yesterday'), thumb=R(ICON)), section='yesterday'))
  dir.Append(Function(DirectoryItem(Top20Browser, title=L('week'), thumb=R(ICON)), section='week'))
  dir.Append(Function(DirectoryItem(Top20Browser, title=L('month'), thumb=R(ICON)), section='month'))
  dir.Append(Function(DirectoryItem(Top20Browser, title=L('alltime'), thumb=R(ICON)), section='alltime'))


  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def HighlightsSectionBrowser(sender, section, page=0):
  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(viewGroup = 'Details', title1 = L('highlights'), title2 = L(section), httpCookies=cookies)

  highlightsPage = HTML.ElementFromURL(GT_HIGHLIGHTS_URL % (section,page), cacheTime=CACHE_HIGHLIGHTS_INTERVAL, errors='ignore')

  videos = highlightsPage.xpath("//div[@class='newestlist_content']/table")

  for video in videos:

    groupTitle = video.xpath(".//div[@class='newestlist_title']/a/text()")[0]
    episodeTitle = video.xpath(".//span[@class='newestlist_subtitle']/a/text()")[0]
    title = groupTitle + ": " + episodeTitle
    description = video.xpath(".//div[@class='newestlist_text']/text()")[0]
    time = video.xpath(".//div[@class='newestlist_time']/div[@class='float_left']/text()")[0]

    thumb = video.xpath(".//img[@class='newestlist_image']")[0].get('src')

    title = re.sub (r'^\s*-\s*', r'', title) # Remove dash
    title = re.sub (r'\\', r'', title ) # Remove escape characters
    description = re.sub (r'^\s*-\s*', r'', title) # Remove dash

    (pageUrl, quality) = GetVideoLink(video)

    if not pageUrl:
      continue

    if quality == 'HD':
      title += ' - HD'

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=time, summary=description, duration='', thumb=thumb), url=pageUrl))


  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def Top20Browser(sender, section, page=0):

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details', title1 = L('highlights'), title2 = L(section))

  top20Page = HTML.ElementFromURL(GT_TOP20_URL % (section,page), cacheTime=CACHE_HIGHLIGHTS_INTERVAL, errors='ignore')

  # Excuse the ugliness of this xpath, it was the only match I could find that would match over each section (yesterday, week, month, alltime)
  videos = top20Page.xpath("//div[substring-after(@id, 'top_media_')='" + section + "']//div[@class='top20_movie_title']/../../..")

  Log (str(len(videos)))

  for video in videos:

    # Most but not all movies have a 'grouptitle', either a game name or a show name
    try:
      groupTitle = str(video.xpath(".//a[@class='gamepage_content_row_title']/text()")[0])
      episodeTitle = str(video.xpath(".//div[@class='top20_movie_title']/a/text()")[0])
      title = groupTitle + ': ' + episodeTitle
    except:
      title = str(video.xpath(".//div[@class='top20_movie_title']/a/text()")[0])

    date = video.xpath(".//div[@class='gamepage_content_row_date']/text()")[0]
    thumb = video.xpath(".//div[@class='top20_content_row_thumb']//img")[0].get('src')


    # Description is at one of two locations
    try:
      description = video.xpath(".//div[@class='top20_content_summary_text']/text()")[0]
    except:
      description = video.xpath(".//div[@class='top20_at_content_summary_text']/text()")[0]

    # Remove BB style tags and their contents from the description
    description = re.sub (r'\[(\w{,3})\].*\[/\1\]', r'', description)
    # Crunch excessive new lines
    description = re.sub (r'\n\s*\n', r'\n\n', description)

    (pageUrl, quality) = GetVideoLink(video)

    if not pageUrl:
      continue

    if quality == 'HD':
      title += ' - HD'

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=pageUrl))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir


def Search(sender, query, nextPageUrl=None, page=1):

  # Browse the 'customizable rss feeds'

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details')
  if page > 1:
    dir.title1 = query
    dir.title2 = L('page') + ' ' + str(page)
  else:
    dir.title1 = L('search')
    dir.title2 = query

  queryString = query.replace(' ', '+')

  if nextPageUrl:
    resultsPage = HTML.ElementFromURL(nextPageUrl, cacheTime=CACHE_SEARCH_INTERVAL, errors='ignore')
  else:
    # First page of results
    resultsPage = HTML.ElementFromURL(GT_SEARCH_URL % queryString, cacheTime=CACHE_SEARCH_INTERVAL, errors='ignore')

  results = resultsPage.xpath("//div[@class='search_movie_row']")

  if len(results) < 1:
    return (MessageContainer(header=L('search'), message=L('nonefound'), title1=L('gt')))

  for result in results:

    title = TidyString(result.xpath(".//div[@class='gamepage_content_row_title']/a/text()")[0])
    subtitle = TidyString(result.xpath(".//div[@class='search_movie_title']/b/text()")[0])
    date = TidyString(result.xpath(".//div[@class='gamepage_content_row_date']/text()")[0])
    subtitle = subtitle + '\n' + date
    description = '\n' + TidyString(result.xpath(".//div[@class='gamepage_content_row_text']/text()")[2])
    thumb = GT_URL + '/' + result.xpath(".//img[@class='preview_content_row_image']")[0].get('src')

    (pageUrl, quality) = GetVideoLink(result)

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=subtitle, summary=description, duration='', thumb=thumb), url=pageUrl))

  # See if there is a next page link
  searchPageLinks = resultsPage.xpath("//a[@class='reviewlist_barlink']")
  if len(searchPageLinks):
    for link in searchPageLinks:
      if re.search (r'Next', link.xpath("./text()")[0]):
        nextPageUrl = GT_SEARCH_BASE + link.get('href')
        dir.Append(Function(DirectoryItem(Search, title=L('nextpage'), summary='', subtitle='', thumb=R(ICON)), sender=None, query=query, nextPageUrl=nextPageUrl, page=page+1))
        break


  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir


