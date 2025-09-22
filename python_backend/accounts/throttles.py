from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class RegisterStartThrottle(AnonRateThrottle):
    scope = "register_start"

class MFAChallengeThrottle(UserRateThrottle):
    scope = "mfa_challenge"