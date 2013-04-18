RE_DURATION = Regex('PT(?P<hours>[0-9]+H)?(?P<minutes>[0-9]+M)?(?P<seconds>[0-9]+S)')
BASE_URL = 'http://www.gametrailers.com/videos-trailers'
FEED_BASE_URL = 'http://www.gametrailers.com/feeds/line_listing_results/video_hub/6bc9c4b7-0147-4861-9dac-7bfe8db9a141/?'

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')
	ObjectContainer.view_group = 'List'
	ObjectContainer.title1 = 'GameTrailers'

@handler('/video/gametrailers', 'GameTrailers')
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(MostViewed), title="Most Viewed Videos"))
	oc.add(DirectoryObject(key=Callback(CategoryBrowser, title="Categories", group="category"), title="Categories"))
	oc.add(DirectoryObject(key=Callback(CategoryBrowser, title="Genres", group="genre"), title="Genres"))
	#oc.add(DirectoryObject(key=Callback(CategoryBrowser, title="Platforms", group="platform"), title="Platforms"))
	oc.add(DirectoryObject(key=Callback(CategoryBrowser, title="Shows", group="show"), title="Shows"))
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.gametrailers", title="Search", summary="Search GameTrailers for videos", prompt="Search for...",))

	return oc

@route('/video/gametrailers/mostviewed')
def MostViewed():

	oc = ObjectContainer(title2="Most Viewed")
	oc.add(DirectoryObject(key=Callback(PopularVideos, index=1, title="Today"), title="Most Viewed Today"))
	oc.add(DirectoryObject(key=Callback(PopularVideos, index=2, title="This Week"), title="Most Viewed This Week"))
	oc.add(DirectoryObject(key=Callback(PopularVideos, index=3, title="This Month"), title="Most Viewed This Month"))
	oc.add(DirectoryObject(key=Callback(PopularVideos, index=4, title="All Time"), title="Most Viewed of All Time"))

	return oc	

@route('/video/gametrailers/popularvideos')
def PopularVideos(index, title):

	oc = ObjectContainer(title2=title)
	data = HTML.ElementFromURL(BASE_URL)

	for item in data.xpath('//ul[@class="video_list"]['+index+']//a[@class="thumbnail"]'):
		url = item.get('href')
		video_title = item.xpath('./img')[-1].get('alt')
		thumb = item.xpath('./img')[-1].get('src')

		oc.add(VideoClipObject(url=url, title=video_title, thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

	return oc

@route('/video/gametrailers/categories')
def CategoryBrowser(title, group):

	oc = ObjectContainer(title2=title)

	for entry in HTML.ElementFromURL(BASE_URL).xpath('//span[@name="'+group+'"]'):
		value = entry.get('value')
		if group == 'show':
			title = entry.text.strip()
		else:
			title = String.Unquote(value)
		oc.add(DirectoryObject(key=Callback(FeedBrowser, feed=value, title=title, group=group), title=title))

	return oc

@route('/video/gametrailers/feed')
def FeedBrowser(feed, title, group, page=None):

	oc = ObjectContainer(title2=title)

	if page:
		page = page.replace('?', '&')
	else:
		page = ''

	feed_url = FEED_BASE_URL + 'sortBy=most_recent&' + group + '=' + feed + page

	for item in HTML.ElementFromURL(feed_url).xpath('//div[@class="video_information"]'):
		contentId = item.get('data-contentId')
		url = item.xpath('.//a[@class="thumbnail"]')[0].get('href')
		video_title = item.xpath('.//meta[@itemprop="name"]')[0].get('content')

		if video_title == 'Review' or video_title == 'Preview':
			video_title = video_title + ' - ' + item.xpath('.//h3/a')[0].text

		thumb = item.xpath('.//meta[@itemprop="thumbnailUrl"]')[0].get('content')
		summary = item.xpath('.//meta[@itemprop="description"]')[0].get('content')
		date = Datetime.ParseDate(item.xpath('.//meta[@itemprop="uploadDate"]')[0].get('content'))
		duration = CalculateDuration(item.xpath('.//meta[@itemprop="duration"]')[0].get('content'))

		oc.add(VideoClipObject(url=url, title=video_title, summary=summary, originally_available_at=date, duration=duration,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb)))

	next_page = HTML.ElementFromURL(feed_url).xpath('.//div[@class="pagination"]//a[@rel="next"]')

	if len(next_page) == 0:
		pass
	else:
		next_page = next_page[0].get('href')
		oc.add(NextPageObject(key=Callback(FeedBrowser, feed=feed, title=title, group=group, page=next_page), title="Next Page"))

	return oc

@route('/video/gametrailers/duration')
def CalculateDuration(timecode):

	try:
		dur = RE_DURATION.search(timecode).groupdict()
		if not dur['hours']:        hours = 0
		else:                       hours = dur['hours'].strip('H')
		if not dur['minutes']:      minutes = 0
		else:                       minutes = dur['minutes'].strip('M')
		if not dur['seconds']:      seconds = 0
		else:                       seconds = dur['seconds'].strip('S')

		duration = ((int(hours)*60 + int(minutes))*60 + int(seconds))*1000
		return duration
	except:
		return None
