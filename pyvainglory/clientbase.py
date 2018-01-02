import datetime

from .errors import VGFilterException
from .const import regions, game_modes


class ClientBase:

    @staticmethod
    def _gamemodecheck(mode):
        if str(mode).title() not in game_modes.keys():
            raise VGFilterException("'{}' is not an accepted gamemode, check the docs for "
                                    "accepted gamemodes.".format(mode))

    @staticmethod
    def _region_check(region):
        if region not in regions.keys():
            raise VGFilterException("'{}' is not an accepted region code, check the docs for "
                                    "accepted regions.".format(region))

    @staticmethod
    def _isocheck(time):
        """
        Check if a time string is compatible with iso8601
        """
        try:
            datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
            return True
        except ValueError:
            return False

    def prepare_match_params(self, offset, limit, after, before, playerids, playernames, gamemodes):
        if all((after, before)):
            if all((isinstance(after, datetime.datetime), isinstance(before, datetime.datetime))):
                if before <= after:
                    raise VGFilterException("'after' must occur at a time before 'before'")
                else:
                    after = after.strftime("%Y-%m-%dT%H:%M:%SZ")
                    before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
            elif all((isinstance(after, str), isinstance(before, str))):
                if not all(map(self._isocheck, (after, before))):
                    raise VGFilterException("'after' or 'before', if instances of 'str', should follow the "
                                            "'iso8601' format '%Y-%m-%dT%H:%M:%SZ'")
                t_after = datetime.datetime.strptime(after, "%Y-%m-%dT%H:%M:%SZ")
                t_before = datetime.datetime.strptime(before, "%Y-%m-%dT%H:%M:%SZ")
                if t_before <= t_after:
                    raise VGFilterException("'after' must occur at a time before 'before'")
            else:
                raise VGFilterException("'after' and 'before' should both be instances "
                                        "of either 'str' or 'datetime.datetime'")
        else:
            if after:
                if isinstance(after, datetime.datetime):
                    after = after.strftime("%Y-%m-%dT%H:%M:%SZ")
                elif not self._isocheck(after):
                    raise VGFilterException("'after', if instance of 'str', should follow the 'iso8601' format "
                                            "'%Y-%m-%dT%H:%M:%SZ'")
            elif before:
                if isinstance(before, datetime.datetime):
                    before = before.strftime("%Y-%m-%dT%H:%M:%SZ")
                elif not self._isocheck(before):
                    raise VGFilterException("'before', if instance of 'str', should follow the 'iso8601' format "
                                            "'%Y-%m-%dT%H:%M:%SZ'")
        # Make sure 'playernames' is a list of 'str's
        if playernames:
            if not all([isinstance(player, str) for player in playernames]):
                raise VGFilterException("'playernames' must be a list of 'str's")
        if gamemodes:
            for mode in gamemodes:
                self._gamemodecheck(mode)
        params = {}
        if offset:
            params['page[offset]'] = offset
        if limit:
            params['page[limit]'] = limit
        if after:
            params['filter[createdAt-start]'] = after
        if before:
            params['filter[createdAt-end]'] = before
        if playernames:
            params['filter[playerNames]'] = ','.join(playernames)
        if playerids:
            params['filter[playerIds]'] = ','.join([str(_id) for _id in playerids])
        if gamemodes:
            params['filter[gameModes]'] = ','.join([str(mode) for mode in gamemodes])

        return params

    @staticmethod
    def prepare_players_params(playerids, usernames):
        if not any((playerids, usernames)):
            raise VGFilterException("One of the filters 'playerids', 'steamids' and 'usernames' is required.")
        try:
            if len(playerids) > 6:
                raise VGFilterException("Only a maximum of 6 playerIDs are allowed for a single"
                                        " request of get_players.")
        except TypeError:
            pass
        try:
            if len(usernames) > 6:
                raise VGFilterException("Only a maximum of 6 usernames are allowed for a single"
                                        " request of get_players.")
        except TypeError:
            pass
        params = {}
        if playerids:
            params['filter[playerIds]'] = ','.join([str(_id) for _id in playerids])
        if usernames:
            params['filter[playerNames]'] = ','.join([str(name) for name in usernames])

        return params

