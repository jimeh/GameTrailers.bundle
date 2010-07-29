import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from Support import *

GT_URL                               = 'http://www.gametrailers.com'
INVISIBLEWALLS_URL                   = 'http://www.gametrailers.com/show/invisible-walls'
CACHE_INVISIBLEWALLS_INTERVAL        = 1800
DEBUG_XML_RESPONSE                   = False
MAX_ITEM_COUNT                       = 20 # Maximum number of items to display per page


def InvisibleWalls(sender, offset=1):

  # Display top menu for InvisibleWalls

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies)
  dir.viewGroup = 'Details'
  dir.title1 = L('channels')
  dir.title2 = L('invisiblewalls')

  invisibleWallsPage = XML.ElementFromURL(INVISIBLEWALLS_URL, isHTML=True, cacheTime=CACHE_INVISIBLEWALLS_INTERVAL, errors='ignore')

  videos = invisibleWallsPage.xpath("//div[@class='basic_container_content']")

  count = 0

  for video in videos:

    count += 1

    if count < offset:
      continue

    if count - offset >= MAX_ITEM_COUNT:
      # Link to next page
      dir.Append(Function(DirectoryItem(InvisibleWalls, title=L('nextpage'), summary='', subtitle='', thumb=R('icon-default.png')), offset=count))
      break

    onclickUrl = video.xpath(".//div[@class='button_container' and contains(@onclick, 'type=mov')]")[0].get('onclick')
    url = GT_URL + re.search(r"'([^']+)'", onclickUrl).group(1)

    title = TidyString(video.xpath(".//div[@class='gameone_title']/text()")[0])
    longTitle = TidyString(video.xpath("./preceding-sibling::*/div[@class='basicinfo_dividertitle']/div/text()")[0])
    date = re.search(r'Posted\s*([^@]+)*\s@', longTitle).group(1)

    description = TidyString(video.xpath(".//div[@class='gameone_description']/text()")[0])
    thumb = video.xpath(".//img")[0].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir




