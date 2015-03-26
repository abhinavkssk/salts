"""
    SALTS XBMC Addon
    Copyright (C) 2014 tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import scraper
import xbmc
import urllib
import urlparse
import re
import xbmcaddon
import time
import json
from salts_lib.db_utils import DB_Connection
from salts_lib import log_utils
from salts_lib.constants import VIDEO_TYPES
from salts_lib.constants import QUALITIES

BASE_URL = 'http://www.cartoonhd.is'

class CartoonHD_Scraper(scraper.Scraper):
    base_url = BASE_URL

    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.db_connection = DB_Connection()
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))

    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])

    @classmethod
    def get_name(cls):
        return 'CartoonHD'

    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        return '[%s] %s' % (item['quality'], item['host'])

    def get_sources(self, video):
        source_url = self.get_url(video)
        sources = []
        if source_url:
            url = urlparse.urljoin(self.base_url, source_url)
            html = self._http_get(url, cache_limit=.5)

            pattern = '<IFRAME\s+SRC="([^"]+)'
            for match in re.finditer(pattern, html, re.DOTALL | re.I):
                url = match.group(1)
                host = urlparse.urlsplit(url).hostname.lower()
                source = {'multi-part': False, 'url': url, 'host': host, 'class': self, 'quality': self._get_quality(video, host, QUALITIES.HIGH), 'views': None, 'rating': None, 'direct': False}
                sources.append(source)

        return sources

    def get_url(self, video):
        return super(CartoonHD_Scraper, self)._default_get_url(video)

    def search(self, video_type, title, year):
        results = []
        html = self. _http_get(self.base_url, cache_limit=8)
        match = re.search("var\s+token\s*=\s*'([^']+)", html)
        if match:
            token = match.group(1)
            
            search_url = urlparse.urljoin(self.base_url, '/ajax/search.php?q=')
            search_url += urllib.quote_plus(title)
            timestamp = int(time.time() * 1000)
            query = {'q': title, 'limit': '100', 'timestamp': timestamp, 'verifiedCheck': token}
            html = self._http_get(search_url, data=query, cache_limit=.25)
            if video_type in [VIDEO_TYPES.TVSHOW, VIDEO_TYPES.EPISODE]:
                media_type = 'TV SHOW'
            else:
                media_type = 'MOVIE'

            if html:
                js_data = json.loads(html)
                for item in js_data:
                    if item['meta'].upper().startswith(media_type):
                        result = {'title': item['title'], 'url': item['permalink'].replace(self.base_url, ''), 'year': ''}
                        results.append(result)
        else:
            log_utils.log('Unable to locate CartoonHD token', xbmc.LOGWARNING)
        return results

    def _get_episode_url(self, show_url, video):
        episode_pattern = 'class="link"\s*href="([^"]+/season/%s/episode/%s/*)"' % (video.season, video.episode)
        return super(CartoonHD_Scraper, self)._default_get_episode_url(show_url, video, episode_pattern)

    def _http_get(self, url, data=None, cache_limit=8):
        return super(CartoonHD_Scraper, self)._cached_http_get(url, self.base_url, self.timeout, data=data, cache_limit=cache_limit)