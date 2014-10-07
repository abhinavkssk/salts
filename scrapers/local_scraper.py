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
import xbmcaddon
import log_utils
import xbmc
from salts_lib.constants import VIDEO_TYPES

from salts_lib.db_utils import DB_Connection
BASE_URL = ''

class Local_Scraper(scraper.Scraper):
    def __init__(self, timeout=scraper.DEFAULT_TIMEOUT):
        self.db_connection = DB_Connection()
        self.base_url = xbmcaddon.Addon().getSetting('%s-base_url' % (self.get_name()))
    
    @classmethod
    def provides(cls):
        return frozenset([VIDEO_TYPES.TVSHOW, VIDEO_TYPES.SEASON, VIDEO_TYPES.EPISODE, VIDEO_TYPES.MOVIE])
    
    @classmethod
    def get_name(cls):
        return 'Local'
    
    def resolve_link(self, link):
        return link

    def format_source_label(self, item):
        pass
    
    def get_sources(self, video):
        pass

    def get_url(self, video):
        temp_video_type=video.video_type
        if video.video_type == VIDEO_TYPES.EPISODE: temp_video_type=VIDEO_TYPES.TVSHOW
        url = None

        results = self.search(temp_video_type, video.title, video.year)
        if results:
            url = results[0]['url']

        if url and video.video_type==VIDEO_TYPES.EPISODE:
            show_url = url
            url = self._get_episode_url(show_url, video)
        
        return url

    def _get_episode_url(self, show_url, video):
        pass

    def search(self, video_type, title, year):
        pass
