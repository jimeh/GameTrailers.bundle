import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

from Support import *

GT_URL                               = 'http://www.gametrailers.com'
SCREWATTACK_URL                      = 'http://www.gametrailers.com/screwattack'
CACHE_SCREWATTACK_INTERVAL           = 1800
DEBUG_XML_RESPONSE                   = False
MAX_ITEM_COUNT                       = 20 # Maximum number of items to display per page


def ScrewAttack(sender):

  # Display top menu for ScrewAttack

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies)
  dir.title1 = L('channels')
  dir.title2 = L('screwattack')


  # The 'id's on the site are wrong
  # nerd = Video Game Vault 
  # vault = Angry Video Game Nerd
  dir.Append(Function(DirectoryItem(ScrewAttackBrowser, title=L('nerd'), thumb=R('icon-default.png')), section='nerd'))
  dir.Append(Function(DirectoryItem(ScrewAttackBrowser, title=L('top10'), thumb=R('icon-default.png')), section='top10'))
  dir.Append(Function(DirectoryItem(ScrewAttackBrowser, title=L('vault'), thumb=R('icon-default.png')), section='vault'))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir


def ScrewAttackBrowser(sender, section, offset=1):

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies)
  dir.title1 = L('screwattack')
  dir.title2 = L(section)
  dir.viewGroup = 'Details'

  screwAttackPage = XML.ElementFromURL(SCREWATTACK_URL, isHTML=True, cacheTime=CACHE_SCREWATTACK_INTERVAL, errors='ignore')

  videos = screwAttackPage.xpath("//div[@id='" + section +"']//div[@class='gamepage_content_row']")

  count = 0

  for video in videos:

    count += 1

    if count < offset:
      continue

    if count - offset >= MAX_ITEM_COUNT:
      # Link to next page
      dir.Append(Function(DirectoryItem(ScrewAttackBrowser, title=L('nextpage'), summary='', subtitle='', thumb=R('icon-default.png')), section=section, offset=count))
      break

    url = GT_URL + video.xpath(".//a[@class='gamepage_content_row_title']")[0].get('href')
    title = TidyString(video.xpath(".//a[@class='gamepage_content_row_title']/text()")[0])
    date = TidyString(video.xpath(".//span[@class='gamepage_content_row_date']/text()")[0])
    description = TidyString(video.xpath(".//span[@class='gamepage_content_row_text']/text()")[0])
    thumb = video.xpath(".//img")[0].get('src')

    # Strip the section name from the title
    title = re.sub (str(L(section))+':?\s*', '', title)

    dir.Append(Function(VideoItem(PlayVideo, title=title, subtitle=date, summary=description, duration='', thumb=thumb), url=url))

  if DEBUG_XML_RESPONSE:
    PMS.Log(dir.Content())
  return dir




