import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from Support import *

GT_URL                               = 'http://www.gametrailers.com'
RETROSPECTIVES_URL                   = 'http://www.gametrailers.com/retrospective/'
CACHE_RETROSPECTIVES_INTERVAL           = 1800
DEBUG_XML_RESPONSE                   = True
MAX_ITEM_COUNT                       = 20 # Maximum number of items to display per page


def Retrospectives(sender):

  # Display top menu for Retrospectives

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies)
  dir.viewGroup = 'Details'
  dir.title1 = L('channels')
  dir.title2 = L('retrospectives')

  retrospectivesPage = XML.ElementFromURL(RETROSPECTIVES_URL, isHTML=True, cacheTime=CACHE_RETROSPECTIVES_INTERVAL, errors='ignore')

  # We need to find both the name for each title and it's ID

  games = retrospectivesPage.xpath("//div[@class='basic_container_text' and not(@style)]")

  for game in games:

    title = TidyString(game.xpath("./div[@class='gamepage_content_row_title']/a/text()")[0])
    title = re.sub (r'\s*Retrospective', r'', title)

    divId = game.xpath("./div[contains(@id, 'episode_segments_')]")[0].get('id')
    gameId = re.sub(r'episode_segments_', r'', divId)

    description = game.xpath("./div[@class='retro_desc']/text()")[0]
    thumb = GT_URL + game.xpath("./div[@class='gamepage_content_row_thumb']/a/img")[0].get('src')

    dir.Append(Function(DirectoryItem(RetrospectivesBrowser, title=title, summary=description, subtitle='', thumb=thumb), title=title, id=gameId))


  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir


def RetrospectivesBrowser(sender, title, id):

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies)
  dir.title1 = L('retrospectives')
  dir.title2 = L(title)

  retrospectivesPage = XML.ElementFromURL(RETROSPECTIVES_URL, isHTML=True, cacheTime=CACHE_RETROSPECTIVES_INTERVAL, errors='ignore')

  parts = retrospectivesPage.xpath("//div[@id='episode_segments_" + id + "']/div[@class='gamepage_content_row']")

  for part in parts:

    url = GT_URL + part.xpath("./div[@class='gamepage_content_row_thumb']/a")[0].get('href')
    title = TidyString(part.xpath("./preceding-sibling::div[position()=1]/div/a/text()")[0])
    date = TidyString(part.xpath(".//div[@class='gamepage_content_row_date']/text()")[0])
    description = TidyString(part.xpath(".//div[@class='gamepage_content_row_text']/text()")[0])
    thumb = part.xpath("./div[@class='gamepage_content_row_thumb']/a/img")[0].get('src')

    # Strip the section name from the title
    #title = re.sub (L(section)+':?\s*', '', title)

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir




