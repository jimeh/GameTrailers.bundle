import re

from Support import *

GT_URL                               = 'http://www.gametrailers.com'
ANTHOLOGY_URL                        = 'http://www.gametrailers.com/game/gt-anthology/11170'
CACHE_ANTHOLOGY_INTERVAL             = 1800
DEBUG_XML_RESPONSE                   = False


def Anthology(sender, offset=1):

  # Display top menu for Anthology

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details', title1 = L('channels'), title2 = L('anthology'))

  anthologyPage = HTML.ElementFromURL(ANTHOLOGY_URL, cacheTime=CACHE_ANTHOLOGY_INTERVAL, errors='ignore')

  videos = anthologyPage.xpath("//div[@id='Features']/div[@style='margin:2px;']")

  for video in videos:

    title = TidyString(video.xpath(".//a[@class='gamepage_content_row_title']/text()")[0])
    date = TidyString(video.xpath(".//span[@class='MovieDate']/text()")[0])
    description = TidyString(video.xpath(".//div[@class='MovieDescription']/text()")[0])

    (url, quality) = GetVideoLink(video)

    if not url:
      continue

    if quality == 'HD':
      title += ' - HD'

    thumb = video.xpath(".//img[@class='gamepage_content_row_image']")[0].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir




