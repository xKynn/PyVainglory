import requests

from .clientbase import ClientBase
from .models import Player, Match, MatchPaginator
from .errors import VGRequestException
from .errors import NotFoundException
from .errors import VGServerException
from .errors import EmptyResponseException


class Client(ClientBase):
    """
    Top level class for user to interact with the API.

    .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

    Parameters
    ----------
    key : str
        The official Vainglory API key.
    session : Optional[requests.Session_]
    """
    def __init__(self, key, session: requests.Session=None):
        self.session = session or requests.Session()
        self.base_url = "https://api.dc01.gamelockerapp.com/shards/{}/"
        self.status_url = "https://api.dc01.gamelockerapp.com/status"
        self.headers = {
            'Authorization': 'Bearer {}'.format(key),
            'Accept': 'application/json'
        }

    def gen_req(self, url, params=None, session=None):
        sess = session or self.session
        with sess.get(url, headers=self.headers,
                      params=params) as req:
            try:
                resp = req.json()
            except (requests.Timeout, requests.ConnectionError):
                raise VGRequestException(req, {})

            if 300 > req.status_code >= 200:
                return resp
            elif req.status_code == 404:
                raise NotFoundException(req, resp)
            elif req.status_code > 500:
                raise VGServerException(req, resp)
            else:
                raise VGRequestException(req, resp)

    def get_status(self):
        """
        Check if the API is up and running

        Returns
        -------
        tuple(createdAt: str, version: str):
        """
        data = self.gen_req(self.status_url)
        return data['data']['attributes']['releasedAt'], data['data']['attributes']['version']

    def match_by_id(self, match_id, region: str=None):
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
        data = self.gen_req("{0}matches/{1}".format(self.base_url.format(region), match_id))
        return Match(data, self.session)

    def get_matches(self, offset: int=None, limit: int=None, after=None, before=None, playerids: list=None,
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

        data = self.gen_req("{}matches".format(self.base_url.format(region)), params=params)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.session, data['included']))
        return MatchPaginator(matches, data['links'], self)

    def player_by_id(self, player_id: int, region: str):
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
        data = self.gen_req("{0}players/{1}".format(self.base_url.format(region), player_id))
        return Player(data['data'])

    def _players(self, playerids, usernames, region, single=False):
        self._region_check(region)
        params = self.prepare_players_params(playerids, usernames)

        print("{0}players".format(self.base_url.format(region)))
        print(params)
        data = self.gen_req("{0}players".format(self.base_url.format(region)), params=params)
        if len(data['data']) == 0:
            raise EmptyResponseException("No Players with the specified criteria were found.")
        if single:
            return Player(data['data'][0])
        else:
            return [Player(player) for player in data['data']]

    def get_players(self, region: str, playerids: list=None, usernames: list=None):
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
        return self._players(playerids, usernames, region)

    def player_by_name(self, username: str, region: str):
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
        return self._players(usernames=[username], region=region, single=True, playerids=None)



