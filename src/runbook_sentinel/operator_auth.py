from __future__ import annotations

import hashlib
import hmac
import re
import secrets

from .errors import OperatorAuthenticationError


AUTHENTICATION_SCHEME = "Sentinel-Capability"
AUTHENTICATION_CHALLENGE = f'{AUTHENTICATION_SCHEME} realm="runbook-sentinel-operator"'
CAPABILITY_PATTERN = re.compile(r"[A-Za-z0-9_-]{43,128}")
CAPABILITY_ERROR = (
    "Operator capability must be 43 through 128 ASCII URL-safe characters"
)
INVALID_CAPABILITY_ERROR = "Operator capability is invalid"
OPERATOR_ID_PATTERN = re.compile(r"operator-[0-9a-f]{16}")
_IDENTITY_ATTESTATION = object()


class AuthenticatedOperator:
    __slots__ = ("_attestation", "identity")

    def __init__(self, identity: str, attestation: object):
        if attestation is not _IDENTITY_ATTESTATION or not OPERATOR_ID_PATTERN.fullmatch(
            identity
        ):
            raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
        self.identity = identity
        self._attestation = attestation

    def __repr__(self) -> str:
        return f"AuthenticatedOperator(identity={self.identity!r})"


def require_authenticated_operator(value: object) -> AuthenticatedOperator:
    if (
        not isinstance(value, AuthenticatedOperator)
        or value._attestation is not _IDENTITY_ATTESTATION
    ):
        raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
    return value


def validate_operator_capability(capability: object) -> str:
    if not isinstance(capability, str) or not CAPABILITY_PATTERN.fullmatch(capability):
        raise ValueError(CAPABILITY_ERROR)
    return capability


def authorization_value(capability: str) -> str:
    validate_operator_capability(capability)
    return f"{AUTHENTICATION_SCHEME} {capability}"


class OperatorAuthenticator:
    __slots__ = ("_operator", "_verifier")

    def __init__(self, capability: str):
        validated = validate_operator_capability(capability)
        capability_bytes = validated.encode("ascii")
        verifier = hashlib.sha256(capability_bytes).digest()
        launch_nonce = secrets.token_bytes(32)
        identity_digest = hashlib.sha256(
            b"runbook-sentinel-operator-id-v1\0" + launch_nonce + capability_bytes
        ).hexdigest()
        self._verifier = verifier
        self._operator = AuthenticatedOperator(
            f"operator-{identity_digest[:16]}", _IDENTITY_ATTESTATION
        )
        del capability_bytes
        del validated

    def authenticate(self, authorization_values: list[str] | tuple[str, ...]) -> AuthenticatedOperator:
        if len(authorization_values) != 1:
            raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
        value = authorization_values[0]
        if not isinstance(value, str):
            raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
        scheme, separator, supplied = value.partition(" ")
        if (
            separator != " "
            or scheme.casefold() != AUTHENTICATION_SCHEME.casefold()
            or not CAPABILITY_PATTERN.fullmatch(supplied)
        ):
            raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
        supplied_verifier = hashlib.sha256(supplied.encode("ascii")).digest()
        if not hmac.compare_digest(supplied_verifier, self._verifier):
            raise OperatorAuthenticationError(INVALID_CAPABILITY_ERROR)
        return self._operator
