import asyncio
import aiohttp

from .clientbase import ClientBase
from .models import Player, AsyncMatch, AsyncMatchPaginator
from .errors import VGRequestException
from .errors import NotFoundException
from .errors import VGServerException
from .errors import EmptyResponseException


class AsyncClient(ClientBase):
    """
    Top level class for user to interact with the API.

    .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

    Parameters
    ----------
    key : str
        The official Vainglory API key.
    session : Optional[requests.Session_]
    """
    def __init__(self, key, session: aiohttp.ClientSession=None):
        self.session = session or aiohttp.ClientSession()
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/{}/"
        self.status_url = "https://api.dc01.gamelockerapp.com/status"
        self.headers = {
            'Authorization': 'Bearer {}'.format(key),
            'Accept': 'application/json'
        }

    async def gen_req(self, url, params=None, session=None):
        sess = session or self.session
        async with sess.get(url, headers=self.headers,
                            params=params) as req:
            try:
                resp = await req.json()
            except (asyncio.TimeoutError, aiohttp.ClientResponseError):
                raise VGRequestException(req, {})

            if 300 > req.status >= 200:
                return resp
            elif req.status == 404:
                raise NotFoundException(req, resp)
            elif req.status > 500:
                raise VGServerException(req, resp)
            else:
                raise VGRequestException(req, resp)

    async def get_status(self):
        """
        Check if the API is up and running

        Returns
        -------
        tuple(createdAt: str, version: str):
        """
        data = await self.gen_req(self.status_url)
        return data['data']['attributes']['releasedAt'], data['data']['attributes']['version']

    async def match_by_id(self, match_id, region: str=None):
        """
        Get a Match by its ID.

        Parameters
        ----------
        match_id : str
        region : str
            The region to look for this match in.

        Returns
        -------
        :class:`pyvainglory.models.Match`
            A match object representing the requested match.
        """
        self._region_check(region)
        data = await self.gen_req("{0}matches/{1}".format(self.base_url.format(region), match_id))
        return AsyncMatch(data, self.session)

    async def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playerids: list=None,
                          playernames: list=None, gamemodes: list=None, region: str=None):
        """
        Access the /matches endpoint and grab a list of matches

        .. _datetime.datetime: https://docs.python.org/3.6/library/datetime.html#datetime-objects

        Parameters
        ----------
        offset : Optional[int]
            The nth number of match to start the page from.
        limit : Optional[int]
            Number of matches to return.
        after : Optional[str or datetime.datetime_]
            Filter to return matches after provided time period, if an str is provided it should follow the **iso8601** format.
        before :  Optional[str or datetime.datetime_]
            Filter to return matches before provided time period, if an str is provided it should follow the **iso8601** format.
        playerids : list(str)
            Filter to only return matches with provided players in them by looking for their player IDs.
        playernames : list(str)
            Filter to only return matches with provided players in them by looking for their playernames.
        gamemodes : list(str)
            Filter to to return only matches that match with the gamemodes in the provided list.
        region : str
            The region to look for matches in.

        Returns
        -------
        :class:`pyvainglory.models.MatchPaginator`
            A MatchPaginator instance representing a get_matches request
        """

        self._region_check(region)

        params = self.prepare_match_params(offset, limit, after, before, playerids, playernames, gamemodes)

        data = await self.gen_req("{}matches".format(self.base_url.format(region)), params=params)
        matches = []
        for match in data['data']:
            matches.append(AsyncMatch(match, self.session, data['included']))
        return AsyncMatchPaginator(matches, data['links'], self)

    async def player_by_id(self, player_id: int, region: str):
        """
        Get a player's info by their ID.

        Parameters
        ----------
        player_id : int
        region : str
            The region to look for this match in.

        Returns
        -------
        :class:`pyvainglory.models.Player`
            A Player object representing the requested player.
        """
        self._region_check(region)
        data = await self.gen_req("{0}players/{1}".format(self.base_url.format(region), player_id))
        return Player(data['data'])

    async def _players(self, playerids, usernames, region, single=False):
        self._region_check(region)
        params = self.prepare_players_params(playerids, usernames)

        data = await self.gen_req("{0}players".format(self.base_url.format(region)), params=params)
        if len(data['data']) == 0:
            raise EmptyResponseException("No Players with the specified criteria were found.")
        if single:
            return Player(data['data'][0])
        else:
            return [Player(player) for player in data['data']]

    async def get_players(self, region: str, playerids: list=None, usernames: list=None):
        """
        Get multiple players' info at once.

        .. _here: https://developer.valvesoftware.com/wiki/SteamID

        Parameters
        ----------
        playerids : list(str)
            A list of playerids, either a `list` of strs or a `list` of ints.
            Max list length is 6.
        usernames : list(str)
            A list of usernames, a `list` of strings, case sensitive.
            Max list length is 6
        region : str
            The region to look for players in.

        Returns
        -------
        list
            A list of :class:`pyvainglory.models.Player`
        """
        return await self._players(playerids, usernames, region)

    async def player_by_name(self, username: str, region: str):
        """
        Get a player's info by their ingame name.

        Parameters
        ----------
        username : str
            Case insensitive username
        region : str
            The region to look for this player in.

        Returns
        -------
        :class:`pyvainglory.models.Player`
            A Player object representing the requested player.
        """
        return await self._players(usernames=[username], region=region, single=True, playerids=None)



