class EmailAlreadyExists(Exception):
    pass


class EmailHasNotBeenVerified(Exception):
    pass


class PhoneAlreadyExists(Exception):
    pass


class PhoneHasNotBeenVerified(Exception):
    pass


class EmailOrPhoneRequired(Exception):
    pass


class UserInactive(Exception):
    pass


class UserAlreadyVerified(Exception):
    pass


class InvalidVerifyToken(Exception):
    pass


class InvalidResetToken(Exception):
    pass


class InvalidToken(Exception):
    pass


class UserNotExists(Exception):
    pass


class UserDeleted(Exception):
    pass


class NewPasswordNotMatch(Exception):
    pass


class InvalidPassword(Exception):
    pass


class OldPasswordMatchNewPassword(Exception):
    pass


class RefreshCountLimitExceeded(Exception):
    pass


class RequiredFacebookId(Exception):
    pass


class RequiredFacebookAccessToken(Exception):
    pass


class FacebookAccountAlreadyExists(Exception):
    pass


class InvalidFacebookIdOrToken(Exception):
    pass


class InvalidFacebookAccessToken(Exception):
    pass


class RequiredGoogleId(Exception):
    pass


class RequiredGoogleAccessToken(Exception):
    pass


class InvalidGoogleIdOrToken(Exception):
    pass


class InvalidGoogleAccessToken(Exception):
    pass


class GoogleAccountAlreadyExists(Exception):
    pass
