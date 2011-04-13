import re
from Support import *

GT_URL                               = 'http://www.gametrailers.com'
COUNTDOWN_URL                        = 'http://www.gametrailers.com/game/gt-countdown/2111'
CACHE_COUNTDOWN_INTERVAL             = 1800
DEBUG_XML_RESPONSE                   = True
MAX_ITEM_COUNT                       = 20 # Maximum number of items to display per page


def Countdown(sender, offset=1):

  # Display top menu for Countdown

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details', title1 = L('channels'), title2 = L('countdown'))

  countdownPage = HTML.ElementFromURL(COUNTDOWN_URL, cacheTime=CACHE_COUNTDOWN_INTERVAL, errors='ignore')

  videos = countdownPage.xpath("//div[@id='Features']/div[@style='margin:2px;']")

  count = 0

  for video in videos:

    count += 1

    if count < offset:
      continue

    if count - offset >= MAX_ITEM_COUNT:
      # Link to next page
      dir.Append(Function(DirectoryItem(Countdown, title=L('nextpage'), summary='', subtitle='', thumb=R('icon-default.png')), offset=count))
      break

    title = TidyString(video.xpath(".//a[@class='gamepage_content_row_title']/text()")[0])
    date = TidyString(video.xpath(".//span[@class='MovieDate']/text()")[0])
    description = TidyString(video.xpath(".//div[@class='MovieDescription']/text()")[0])

    (url, quality) = GetVideoLink(video)

    if not url:
      count -= 1
      continue

    if quality == 'HD':
      title += ' - HD'

    thumb = video.xpath(".//img[@class='gamepage_content_row_image']")[0].get('src')

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir




