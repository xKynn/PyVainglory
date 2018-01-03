import datetime

from collections import namedtuple
from urllib.parse import urlparse
from urllib.parse import parse_qs
from .errors import VGPaginationError
from .const import skins, regions, game_modes, items


def _get_object(lst, _id):
    """
    Internal function to grab data referenced inside response['included']
    """
    for item in lst:
        if item['id'] == _id:
            return item


class BaseVGObject:
    """
    A base object for most data classes
    
    Attributes
    ----------
    id : str
        A general unique ID for each type of data.
    """
    __slots__ = ['id']

    def __init__(self, data):
        self.id = data['id']


games_played = namedtuple('games_played', 'battle_royale blitz casual ranked onslaught')
current_elo = namedtuple('current_elo', 'blitz ranked')


class Player(BaseVGObject):
    """
    A class that holds general user data, if this is through a Match, this will not have
    name, picture and title, only an ID
    
    Attributes
    ----------
    id : str
        A general unique ID for each type of data.
    name : str
        The player's name
    region : tuple(region_code: str, friendly_region_name: str)
        The region id for this Player's region, ex: 'sg', 'na', etc.
    elo_history : dict
        The player's past highest elo for seasons 4 through 9.
    karma_level : tuple(karma: int, text_karma: str)
        The karma level for this player, the tuple provides a text translation for each karma level, i.e 0, 1 and 2.
    account_level : int
        The Player's account's level.
    lifetime_gold : int
        Total amount of gold this player has earned since the account was created.
    games_played : namedtuple('games_played', 'battle_royale blitz casual ranked onslaught')
        The attributes can be accessed using dotted access, ex: games_played.battle_royale.
    skill_tier : int
        The Player's account's current skill tier.
    win_streak : int
        The Player's current win streak.
    wins : int
        Total amount of wins the player has had since the account was created.
    xp : int
        The account's XP level.

    Optional
    --------
    guild_tag : str
        The account's guild's tag. Will exist only if this Player object comes through the /players endpoint.
    current_elo : int
        The account's current elo rating. Will exist only if this Player object comes through the /players endpoint.

    """
    __slots__ = ['id', 'name', 'region', 'elo_history', 'karma_level', 'account_level', 'lifetime_gold', 'loss_streak',
                 'games_played', 'skill_tier', 'win_streak', 'wins', 'xp', 'guild_tag', 'current_elo']

    def __init__(self, data):
        super().__init__(data)
        if data.get('attributes'):
            self.name = data['attributes']['name']
            self.region = data['attributes']['shardId'], regions[data['attributes']['shardId']]
            stats = data['attributes']['stats']
            self.elo_history = {season: stats['elo_earned_season_{}'.format(season)] for season in range(4, 10)}
            if stats['karmaLevel'] == 2:
                self.karma_level = 2, "Great Karma"
            elif stats['karmaLevel'] == 1:
                self.karma_level = 1, "Good Karma"
            else:
                self.karma_level = 0, "Bad Karma"
            self.account_level = stats['level']
            self.lifetime_gold = stats['lifetimeGold']
            if 'gamesPlayed' not in stats:
                self.games_played = games_played(stats['played_aral'], stats['played_blitz'], stats['played_casual'],
                                                 stats['played_ranked'], stats.get('played_blitz_rounds'))
            else:
                self.games_played = games_played(stats['gamesPlayed']['aral'], stats['gamesPlayed']['blitz'],
                                                 stats['gamesPlayed']['casual'], stats['gamesPlayed']['ranked'],
                                                 stats['gamesPlayed']['blitz_rounds'])
            self.skill_tier = stats['skillTier']
            self.win_streak = stats['winStreak']
            self.wins = stats['wins']
            self.xp = stats['xp']

            # These may or may not exist depending on which endpoint data is coming from
            if 'guildTag' in stats:
                self.guild_tag = stats['guildTag']
            if 'rankPoints' in stats:
                self.current_elo = current_elo(stats['rankPoints']['blitz'], stats['rankPoints']['ranked'])

    def elo_for_season(self, elo: int):
        if elo in self.elo_history.keys():
            return self.elo_history[elo]
        else:
            raise Exception('Elo data is available only for seasons 4 through 9.')

    def __repr__(self):
        return "<Player: id={}>".format(self.id)


class Participant(BaseVGObject):
    """
    A class that holds data about a participant in a match.
        
    Attributes
    ----------
    id : str
        A general unique ID for each type of data.
    actor : str
    region : tuple(region_code: str, friendly_region_name: str)
    assists : int
    crystal_mines_captured : int
    deaths : int
    farm : int
    first_time_afk : bool
    gold : int
    gold_mines_captured : int
    items_bought : dict()
    items_sold : dict()
    items_used : dict()
    final_build : list(str)
    jungle_kills : int
    kills : int
    krakens_captured : int
    minion_kills : int
    skin : str
    turrets_captured : int
    player : :class:`Player`
    """
    __slots__ = ['actor', 'region', 'assists', 'crystal_mines_captured', 'deaths', 'farm', 'first_time_afk', 'gold',
                 'gold_mines_captured', 'items_bought', 'items_sold', 'items_used', 'final_build', 'jungle_kills',
                 'kills', 'krakens_captured', 'minion_kills', 'skin', 'turrets_captured','went_afk', 'winner', 'player']

    def __init__(self, participant, included):
        super().__init__(participant)
        data = _get_object(included, participant['id'])
        self.actor = data['attributes']['actor']
        self.region = data['attributes']['shardId'], regions[data['attributes']['shardId']]
        stats = data['attributes']['stats']
        self.assists = stats['assists']
        self.crystal_mines_captured = stats['crystalMineCaptures']
        self.deaths = stats['deaths']
        self.farm = stats['farm']
        self.first_time_afk = True if stats['firstAfkTime'] == 1 else False
        self.gold = stats['gold']
        self.gold_mines_captured = stats['goldMineCaptures']

        self.items_bought = {items[name.strip('*')]: quant for name, quant in stats['itemGrants'].items()}
        self.items_sold = {items[name.strip('*')]: quant for name, quant in stats['itemSells'].items()}
        self.items_used = {items[name.strip('*')]: quant for name, quant in stats['itemUses'].items()}

        self.final_build = stats['items']
        self.jungle_kills = stats['jungleKills']
        self.kills = stats['kills']
        self.krakens_captured = stats['krakenCaptures']
        self.minion_kills = stats['minionKills']

        if stats['skinKey'] in skins:
            self.skin = skins[stats['skinKey']]
        else:
            self.skin = stats['skinKey']

        self.turrets_captured = stats['turretCaptures']
        self.player = Player(data['relationships']['player']['data'])

    def __repr__(self):
        return "<Participant: id={0.id} region={0.region} actor={0.actor} bot={1}>".format(self, True if not
                                                                                           self.player else False)


class Roster(BaseVGObject):
    """
    A class that holds data about one of the two teams in a match.

    Attributes
    ----------
    id : str
        A general unique ID for each type of data.
    region : tuple(region_code: str, friendly_region_name: str)
        The region shard on which this roster data resides.
    aces : int
    gold : int
    hero_kills : int
    krakens_captured : int
    side : str
        This is in the format of 'side/color', ex: 'left/blue'.
    turret_kills : int
    turrets_remaining : int
    won : bool
        Signifies if the roster won a match.
    participants : list(:class:`Participant`)
       A list of :class:`Participant` representing players that are part of the roster.
    """
    __slots__ = ['region', 'aces', 'won', 'gold', 'hero_kills', 'krakens_captured', 'side', 'turret_kills',
                 'turrets_remaining', 'participants']

    def __init__(self, roster, included):
        super().__init__(roster)
        data = _get_object(included, roster['id'])
        self.region = data['attributes']['shardId'], regions[data['attributes']['shardId']]
        stats = data['attributes']['stats']
        self.aces = stats['acesEarned']
        self.gold = stats['gold']
        self.hero_kills = stats['heroKills']
        self.krakens_captured = stats['krakenCaptures']
        self.side = stats['side']
        self.turret_kills = stats['turretKills']
        self.turrets_remaining = stats['turretsRemaining']
        self.won = True if data['attributes']['won'] == 'true' else False

        self.participants = []
        for participant in data['relationships']['participants']['data']:
            self.participants.append(Participant(participant, included))

    def __repr__(self):
        return "<Roster: id={0.id} region={0.region} won={0.won}>".format(self)


class MatchBase(BaseVGObject):
    """
    A class that holds data for a match.

    .. _datetime.datetime: https://docs.python.org/3.6/library/datetime.html#datetime-objects
    .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session
    .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

    Attributes
    ----------
    id : str
        A general unique ID for each type of data.
    created_at : datetime.datetime_
        Time when the match was created.
    duration : int
        The match's duration in seconds.
    game_mode : tuple(mode_code: str, friendly_mode_name: str)
        The gamemode this match was of.
    patch : str
        The Vainglory patch version this match was played on.
    region : tuple(region_code: str, friendly_region_name: str)
        The region shard on which this match data resides.
    game_end_reason : str
        Can either be 'victory' or 'surrender'.
    rosters : list(:class:`Roster`)
        A list of :class:`Roster` objects representing rosters taking part in the match.
    spectators : list(:class:`Participant`)
        A list of :class:`Participant` objects representing spectators.
    telemetry_url : str
        URL for the telemetry file for this match
    session : aiohttp.ClientSession_ or requests.Session_
        Depends on which class extends MatchBase, AsyncClient or normal Client, respectively.
    """
    __slots__ = ['created_at', 'duration', 'game_mode', 'patch', 'region', 'game_end_reason', 'telemetry_url',
                 'rosters', 'spectators', 'session']

    def __init__(self, data, session, included=None):
        included = included or data['included']
        data = data if included else data['data']
        super().__init__(data)
        self.created_at = datetime.datetime.strptime(data['attributes']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
        self.duration = data['attributes']['duration']
        self.game_mode = data['attributes']['gameMode'], game_modes[data['attributes']['gameMode']]
        self.patch = data['attributes']['patchVersion']
        self.region = data['attributes']['shardId'], regions[data['attributes']['shardId']]
        self.game_end_reason = data['attributes']['stats']['endGameReason']
        self.rosters = []
        for roster in data['relationships']['rosters']['data']:
            self.rosters.append(Roster(roster, included))
        self.spectators = []
        for participant in data['relationships']['spectators']['data']:
            self.spectators.append(Participant(participant, included))
        self.telemetry_url = _get_object(included,
                                         data['relationships']['assets']['data'][0]['id'])['attributes']['URL']
        self.session = session


class AsyncMatch(MatchBase):
    """
    Extends :class:`MatchBase` to add async :meth:`get_telemetry`.
    """
    def __init__(self, data, session, included=None):
        super().__init__(data, session, included)

    def __repr__(self):
        return "<AsyncMatch: id={0.id} region={0.region}>".format(self)

    async def get_telemetry(self, session=None):
        """
        Get telemetry data for a match.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to request telemetry data.

        Returns
        -------
        `dict`
            Match telemetry data
        """
        sess = session or self.session
        async with sess.get(self.telemetry_url, headers={'Accept': 'application/json'}) as resp:
            data = await resp.json()

        # After understanding the telemetry structure, to provide it as usable data is going to be a tough ordeal,
        # but one that can be looked into later
        return data


class Match(MatchBase):
    """
    Extends :class:`MatchBase` to add :meth:`get_telemetry`
    """
    def __init__(self, data, session, included=None):
        super().__init__(data, session, included)

    def __repr__(self):
        return "<Match: id={0.id} region={0.region}>".format(self)

    def get_telemetry(self, session=None):
        """
        Get telemetry data for a match.

        .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

        Parameters
        ----------
        session : Optional[requests.Session_]
            Optional session to use to request telemetry data.

        Returns
        -------
        `dict`
            Match telemetry data
        """
        sess = session or self.session
        with sess.get(self.telemetry_url, headers={'Accept': 'application/json'}) as resp:
            data = resp.json()

        # After understanding the telemetry structure, to provide it as usable data is going to be a tough ordeal,
        # but one that can be looked into later
        return data


class Paginator:
    """
    Returned only by pyvainglory's client classes.
    """
    __slots__ = ['matches', 'next_url', 'first_url', 'client', 'prev_url', 'offset']

    def __init__(self, matches, data, client):
        self.matches = matches
        self.next_url = data.get('next')
        self.first_url = data.get('first')
        self_params = parse_qs(urlparse(data['self'])[4])
        self.offset = self_params.get('page[offset]', 0)
        if self.offset:
            self.offset = self.offset[0]
        self.prev_url = data.get('prev')
        self.client = client

    def __getitem__(self, item):
        return self.matches[item]

    def __iter__(self):
        return iter(self.matches)


class AsyncMatchPaginator(Paginator):
    """
    Returned only by the *get_matches* method of the async client.

    Attributes
    ----------
    matches : list(:class:`AsyncMatch`)
        A list of matches.
    """
    def __init__(self, matches, data, client):
        super().__init__(matches, data, client)

    def __repr__(self):
        return "<AsyncMatchPaginator: offset={} next={} prev={}>".format(self.offset, bool(self.next_url),
                                                                         bool(self.prev_url))

    async def _matchmaker(self, url, sess=None):
        data = await self.client.gen_req("{}matches".format(url), session=sess)
        matches = []
        for match in data['data']:
            matches.append(AsyncMatch(match, self.client.session, data['included']))
        print(matches)
        self.__init__(matches, data['links'], self.client)
        return matches

    async def next(self, session=None):
        """
        Move to the next page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        VGPaginationError
            The current page is the last page of results
        """
        if self.next_url:
            matches = await self._matchmaker(self.next_url, session)
            return matches
        else:
            raise VGPaginationError("This is the last page")

    async def first(self, session=None):
        """
        Move to the first page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        """
        if self.first_url:
            matches = await self._matchmaker(self.first_url, session)
            return matches
        else:
            raise VGPaginationError('This is the first page')

    async def prev(self, session=None):
        """
        Move to the previous page of matches.

        .. _aiohttp.ClientSession: https://aiohttp.readthedocs.io/en/stable/client_reference.html#client-session

        Parameters
        ----------
        session : Optional[aiohttp.ClientSession_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        VGPaginationError
            The current page is the first page of results
        """
        if self.prev_url:
            matches = await self._matchmaker(self.prev_url, session)
            return matches
        else:
            raise VGPaginationError("This is the first page")


class MatchPaginator(Paginator):
    """
    Returned only by the *get_matches* method of the client.

    Attributes
    ----------
    matches : list(:class:`Match`)
        A list of matches.
    """
    def __init__(self, matches, data, client):
        super().__init__(matches, data, client)

    def __repr__(self):
        return "<MatchPaginator: offset={} next={} prev={}>".format(self.offset, bool(self.next_url),
                                                                    bool(self.prev_url))

    def _matchmaker(self, url, sess=None):
        data = self.client.gen_req("{}matches".format(url), session=sess)
        matches = []
        for match in data['data']:
            matches.append(Match(match, self.client.session, data['included']))
        print(matches)
        self.__init__(matches, data['links'], self.client)
        return matches

    def next(self, session=None):
        """
        Move to the next page of matches.

        .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

        Parameters
        ----------
        session : Optional[requests.Session_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        VGPaginationError
            The current page is the last page of results
        """
        if self.next_url:
            matches = self._matchmaker(self.next_url, session)
            return matches
        else:
            raise VGPaginationError("This is the last page")

    def first(self, session=None):
        """
        Move to the first page of matches.

        .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

        Parameters
        ----------
        session : Optional[requests.Session_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        """
        if self.first_url:
            matches = self._matchmaker(self.first_url, session)
            return matches
        else:
            raise VGPaginationError('This is the first page')

    def prev(self, session=None):
        """
        Move to the previous page of matches.

        .. _requests.Session: http://docs.python-requests.org/en/master/api/#request-sessions

        Parameters
        ----------
        session : Optional[requests.Session_]
            Optional session to use to make this request.

        Returns
        -------
        `list`
            A list of :class:`Match`.

        Raises
        ------
        VGPaginationError
            The current page is the first page of results
        """
        if self.prev_url:
            matches = self._matchmaker(self.prev_url, session)
            return matches
        else:
            raise VGPaginationError("This is the first page")
