import re

from Support import *

# Bonus Round channel for GameTrailers plugin

GT_URL                               = 'http://www.gametrailers.com'
BONUSROUND_EPISODES_URL              = 'http://www.gametrailers.com/br_showpage_ajaxfuncs.php'
MOSES_URL_BASE                       = 'http://moses.gametrailers.com/moses/gttv_xml'
CACHE_GTTV_INTERVAL                  = 1800
DEBUG_XML_RESPONSE                   = False


def BonusRound(sender, pageNumber=1):

  # Display top menu for Bonus Round

  cookies = HTTP.GetCookiesForURL(GT_URL)
  dir = MediaContainer(httpCookies=cookies, viewGroup = 'Details')
  if pageNumber==1:
    dir.title1 = L('channels')
    dir.title2 = L('bonusround')
  else:
    dir.title1 = L('bonusround')
    dir.title2 = L('page') + ' ' + str(pageNumber)

  values = {
    'do' : 'get_playlist_page',
    'page' : pageNumber
  }

  episodesPage = HTML.ElementFromURL(BONUSROUND_EPISODES_URL, values=values, cacheTime=CACHE_GTTV_INTERVAL, errors='ignore')

  # Episodes are in two styles, process the new look ones first

  newEpisodes = episodesPage.xpath("//div[@class='br_episode_container']")

  for episode in newEpisodes:

    if Prefs.Get('quality-key') == 'SD Only':
      url = GT_URL + episode.xpath(".//a[@class='media_hdsdbutton']")[0].get('href')
    else:
      url = GT_URL + episode.xpath(".//a[@class='media_hdsdbutton']")[1].get('href')

    thumb = GT_URL + episode.xpath(".//img")[0].get('src')
    title = TidyString(episode.xpath(".//div[@class='br_episode_title']/text()")[0])
    description = TidyString(episode.xpath(".//div[@class='br_episode_summary']/text()")[0]) 

    # Add information on available parts

    description = "\n" + description

    parts = episode.xpath(".//div[@class='br_part_name']")
    parts.reverse()
    

    for part in parts:
      name = part.xpath(".//b/text()")[0]
      date = part.xpath(".//span/text()")[0]
      description = name + ' ' + date + "\n" + description

    dir.Append(Function(VideoItem(PlayBonusRound, title=title, subtitle='', summary=description, duration='', thumb=thumb), url=url))

  oldEpisodes = episodesPage.xpath("//div[@class='br_episode_container_old']")

  for episode in oldEpisodes:

    if Prefs['quality-key'] == 'SD Only':
      url = GT_URL + episode.xpath(".//a[@class='media_hdsdbutton']")[0].get('href')
    else:
      url = GT_URL + episode.xpath(".//a[@class='media_hdsdbutton']")[1].get('href')

    thumb = GT_URL + episode.xpath(".//img")[0].get('src')
    title = TidyString(episode.xpath(".//div[@class='br_episode_title']/text()")[0])
    description = TidyString(episode.xpath(".//div[@class='br_episode_summary']/text()")[0])

    dir.Append(Function(VideoItem(PlayBonusRound, title=title, summary=description, duration='', thumb=thumb), url=url))



  # Check for next page link

  if len ( episodesPage.xpath("//a[contains( text(), 'Next')]") ):
    # We have a next page link
    nextPageNumber = pageNumber + 1
    dir.Append(Function(DirectoryItem(BonusRound, title=L('nextpage'), thumb=R('icon-default.png')), pageNumber=nextPageNumber))

  if DEBUG_XML_RESPONSE:
    Log(dir.Content())
  return dir

