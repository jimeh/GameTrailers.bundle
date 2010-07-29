import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

# Support functioons for GameTrailers

GT_URL                               = 'http://www.gametrailers.com'
GT_MEDIATYPES                        = [ 'mov', 'wmv', 'mp4' ]
CACHE_VIDEOPAGE_INTERVAL             = 100000

def PlayVideo(sender, url):

  # BonusRound needs it's own 'play' fuction (to parse the html), so dispatch that first
  Log("Playing video "+url)
  if re.search (r'bonusround', url):
    return PlayBonusRound(None, url)

  else:

    # Get the page for the video and extract the quicktime movie

    page = XML.ElementFromURL(url, isHTML=True, cacheTime=0, errors='ignore')
    mediaUrls = page.xpath("//div[@id='MediaDownload']/div/span[@class='Downloads']/a")
    mediaType = Prefs.Get('mediatype-key')

    # Look for the requested mediaType

    targetUrl = None

    for mediaUrl in mediaUrls:
      Log("URL:"+mediaUrl.get('href'))
      if re.search(mediaType, mediaUrl.get('href')):
        targetUrl = mediaUrl.get('href')
    
    # If we didn't find anything fallback to 'mov'

    if targetUrl == None:

      for mediaUrl in mediaUrls:
        if re.search(r'mov', mediaUrl.get('href')):
          targetUrl = mediaUrl.get('href')
          
    return Redirect(targetUrl)

def PlayBonusRound(sender, url):

  # Pull the requested url and find the flv

  episodePage = XML.ElementFromURL(url, isHTML=True, cacheTime=CACHE_VIDEOPAGE_INTERVAL, errors='ignore')
  playerCode = episodePage.xpath("//div[@class='gttv_page']/embed")[0].get('flashvars')
  metadataUrl = re.search( r"filename=([^&]+)&", playerCode).group(1)
  metadataPage = XML.ElementFromURL(metadataUrl, isHTML=False, cacheTime=CACHE_VIDEOPAGE_INTERVAL)

  if Prefs.Get('quality-key') == 'SD Only':
    flvUrl = metadataPage.xpath("//sd/flv/text()")[0]
  else:
    flvUrl = metadataPage.xpath("//hd/flv/text()")[0]

  return Redirect(flvUrl)


def GetVideoLink(xml):

    # Extracts the URL to the page containing video matching the users preference
    # Returns None if no videa of the required quality can be found

    # See if content is available in HD & SD or just SD and select according to preferences

    hdsdLinks = xml.xpath(".//div[substring-after(@class,'format_')='SDHD']/a")
    sdLinks = xml.xpath(".//div[substring-after(@class,'format_')='SD']/a")

    # If we have sdLinks then the video only has SD
    if len(sdLinks) > 0:
      # Check user had not requested 'HD Only'
      if Prefs.Get('quality-key') == 'HD Only':
        # We have no content for this user
        pageUrl = None
        quality = None
      else:
        pageUrl = sdLinks[0].get('href')
        quality = 'SD'
    else:
      # We have both SD and HD
      if Prefs.Get('quality-key') == 'SD Only':
        # SD Link
        pageUrl = hdsdLinks[1].get('href')
        quality = 'SD'
      else:
        # HD Link
        pageUrl = hdsdLinks[0].get('href')
        quality = 'HD'

    if pageUrl is not None:
      if pageUrl.find (GT_URL) == -1:
        pageUrl = GT_URL + pageUrl

    return (pageUrl, quality)



############################

def TidyString(stringToTidy):
  # Function to tidy up strings works ok with unicode, 'strip' seems to have issues in some cases so we use a regex
  if stringToTidy:
    # Strip new lines
    stringToTidy = re.sub(r'\n', r' ', stringToTidy)
    # Strip leading / trailing spaces
    stringSearch = re.search(r'^\s*(\S.*?\S?)\s*$', stringToTidy)
    if stringSearch == None:
      return ''
    else:
      return stringSearch.group(1)
  else:
    return ''

