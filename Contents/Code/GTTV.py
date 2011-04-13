import re
from Support import *

GT_URL                               = 'http://www.gametrailers.com'
GTTV_EPISODES_URL                     = 'http://www.gametrailers.com/gttv_ajaxfuncs.php'
MOSES_URL_BASE                       = 'http://moses.gametrailers.com/moses/gttv_xml'
CACHE_GTTV_INTERVAL           = 1800
DEBUG_XML_RESPONSE                   = False


def GTTV(sender, pageNumber=1):

  # Display top menu for GTTV

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details')
  if pageNumber==1:
    dir.title1 = L('channels')
    dir.title2 = L('gttv')
  else:
    dir.title1 = L('gttv')
    dir.title2 = L('page') + ' ' + str(pageNumber)

  values = {
    'do' : 'get_list_page',
    'page' : pageNumber
  }

  episodesPage = HTML.ElementFromURL(GTTV_EPISODES_URL, values=values, cacheTime=CACHE_GTTV_INTERVAL, errors='ignore')

  episodes = episodesPage.xpath("//div[@class='gttv_episode']")

  for episode in episodes:

    url = episode.xpath(".//a")[0].get('href')
    thumb = episode.xpath(".//img")[0].get('src')
    title = TidyString(episode.xpath(".//div[contains(@class, 'title')]/text()")[0])
    date = TidyString(episode.xpath(".//div[contains(@class, 'title')]/text()")[1])
    description = TidyString(episode.xpath(".//div[contains(@class, 'description')]/text()")[0])
    description = re.sub(r'\\', r'', description)

    # Get more metadata for each chapter

    episodePage = HTML.ElementFromURL(url, cacheTime=CACHE_GTTV_INTERVAL, errors='ignore')
    chapters = episodePage.xpath("//div[@id='gttv_chapters']/div[@class='gttv_chapter']")

    for chapter in chapters:

      chapterTitle = TidyString(chapter.xpath(".//div[contains(@class, 'title')]/text()")[0])
      chapterDescription = TidyString(chapter.xpath(".//div[contains(@class, 'description')]/text()")[0])
      chapterDescription = re.sub(r'\\', r'', chapterDescription)

      description += "\n\n" + chapterTitle + "\n" + chapterDescription

    dir.Append(Function(VideoItem(PlayGTTV, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  # Check for next page link

  if len ( episodesPage.xpath("//a[contains( text(), 'Next')]") ):
    # We have a next page link
    nextPageNumber = pageNumber + 1
    dir.Append(Function(DirectoryItem(GTTV, title=L('nextpage'), thumb=R('icon-default.png')), pageNumber=nextPageNumber))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

def PlayGTTV(sender, url):

  # Pull the requested url and find the flv

  episodePage = HTML.ElementFromURL(url, cacheTime=CACHE_GTTV_INTERVAL, errors='ignore')

  playerCode = episodePage.xpath("//div[@id='gttv_player']/script/text()")[0]

  metadataUrl = MOSES_URL_BASE + re.search( r"'filename', '([^']+)'", playerCode).group(1)
  # TODO Replace with String.URLEncode when new framework is released
  metadataUrl = re.sub(r' ', r'%20', metadataUrl)

  metadataPage = XML.ElementFromURL(metadataUrl, cacheTime=CACHE_GTTV_INTERVAL)
  
  if Prefs['quality-key'] == 'SD Only':
    flvUrl = metadataPage.xpath("//sd/flv/text()")[0]
  else:
    flvUrl = metadataPage.xpath("//hd/flv/text()")[0]


  return Redirect(flvUrl)

