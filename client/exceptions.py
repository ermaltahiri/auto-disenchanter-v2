class ClientException(Exception):
    pass


class ConsentRequiredException(ClientException):
    pass


class AuthenticationFailureException(ClientException):
    pass


class AccountBannedException(ClientException):
    def __init__(self, ban_reason='Unspecified'):
        self.ban_reason = ban_reason


class RateLimitedException(ClientException):
    pass


class NameChangeRequiredException(ClientException):
    pass


class AccountChangeNeededException(ClientException):
    pass


class LogoutNeededException(ClientException):
    pass


class LoginUnsuccessfulException(ClientException):
    pass


class LootRetrieveException(ClientException):
    pass


class RegionMissingException(ClientException):
    pass
