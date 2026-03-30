#!/usr/bin/env python3
"""Interface skeleton for the true missing quark relative-sheet orbit provider."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class CanonicalToken:
    token: str


@dataclass(frozen=True)
class CKMTuple:
    theta_12: float
    theta_23: float
    theta_13: float
    delta_ckm: float
    jarlskog: float


@dataclass(frozen=True)
class OrbitElement:
    sigma_id: str
    canonical_token: CanonicalToken
    ckm: CKMTuple


class SigmaUDOrbitProvider(Protocol):
    def enumerate_relative_sheets_d12(self) -> Sequence[CanonicalToken]:
        raise NotImplementedError(
            "Current local corpus does not expose finite Sigma_ud representatives."
        )

    def evaluate_relative_sheet_ckm(self, token: CanonicalToken) -> CKMTuple:
        raise NotImplementedError(
            "Current local corpus does not expose a sigma -> CKM evaluator."
        )


def build_sigma_ud_orbit(provider: SigmaUDOrbitProvider) -> list[OrbitElement]:
    orbit: list[OrbitElement] = []
    for idx, token in enumerate(provider.enumerate_relative_sheets_d12()):
        orbit.append(
            OrbitElement(
                sigma_id=f"sigma_{idx}",
                canonical_token=token,
                ckm=provider.evaluate_relative_sheet_ckm(token),
            )
        )
    return orbit

