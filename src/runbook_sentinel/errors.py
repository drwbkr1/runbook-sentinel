class SentinelError(Exception):
    """Base error for bounded runtime failures."""


class NotFoundError(SentinelError):
    pass


class ApprovalError(SentinelError):
    pass


class OperatorAuthenticationError(ApprovalError):
    pass


class ReplayRejected(ApprovalError):
    pass


class PolicyRejected(SentinelError):
    pass
