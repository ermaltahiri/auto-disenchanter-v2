class ClientException(Exception):
    pass

# class AlreadyInGame(ClientException):
#     pass


class ConsentRequiredException(ClientException):
    pass


class AuthenticationFailureException(ClientException):
    pass


class AccountBannedException(ClientException):
    def __init__(self, ban_reason='Unspecified'):
        self.ban_reason = ban_reason


# class QueueLockoutException(ClientException):

#     def __init__(self, until=None):
#         self.until = until


class RateLimitedException(ClientException):
    pass


class NameChangeRequiredException(ClientException):
    pass


# class BadUsernameException(ClientException):
#     pass


class AccountChangeNeededException(ClientException):
    pass


class LogoutNeededException(ClientException):
    pass


class LoginUnsuccessfulException(ClientException):
    pass


class LootRetrieveException(ClientException):
    pass


# class BuggedLobbyException(ClientException):
#     pass


# class FwotdDataParseException(ClientException):
#     pass


# class BotContinueException(ClientException):
#     pass


# class BotStopException(ClientException):
#     pass


class RegionMissingException(ClientException):
    pass


# class PatchingRequiredException(ClientException):
#     def __init__(self, patcher_state):
#         Exception.__init__(self)
#         self.patcher_state = patcher_state


# class DodgeChampSelectException(ClientException):
#     def __init__(self, unrecognized_summoners=""):
#         self.unrecognized_summoners = unrecognized_summoners
