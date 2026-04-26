# OPH Lab-Facing Predictions

This page collects OPH quantities that can be compared directly by precision
laboratories. It separates values that are already emitted on declared OPH
surfaces from quantities whose proof or measurement protocol is still open.

## Claim Tiers

- **Ready comparison**: OPH emits a number on a declared surface. Future
  measurements can compare directly once the experimental scheme matches the
  stated observable.
- **Conditional target**: OPH identifies a fixed-point or continuation target,
  but a final certificate or scheme bridge is still pending.
- **Not yet a prediction**: the current derivation has a declared gap.

## Fine-Structure Constant

The values in this subsection are comparison targets for future metrology.
They are not solver inputs; the `P`-closure code has no built-in inverse-alpha
constant.

| Quantity | OPH target | Status | Verification route |
| --- | ---: | --- | --- |
| Thomson-limit inverse fine-structure constant | `137.035999177` | External comparison target: numerical `P`-closure witness, interval/contraction certificate still being hardened | Independent atom-recoil, electron `g-2`, quantum Hall, and least-squares constant updates |
| Pixel ratio from that Thomson target | `P = 1.630968209403959...` | Conditional target | Same fine-structure route, mapped through `P = phi + alpha sqrt(pi)` |

The immediate prediction is stability: future independent determinations of
the Thomson-limit inverse fine-structure constant should remain compatible with
`137.035999177` within their stated uncertainties. A sharper OPH-only error bar
requires the interval certificate and a theorem-grade zero-momentum transport
certificate.

## CERN-Facing Electroweak Rows

| Observable | OPH value | Status | Main comparison surface |
| --- | ---: | --- | --- |
| `W` pole mass | `80.37700001539531 GeV` | Ready comparison on the target-free D10 public row | LHC/HL-LHC and future threshold-scan electroweak fits |
| `W` frozen validation sidecar | `80.377 GeV` | Compare-only sidecar | Same experimental inputs, kept separate from the public theorem row |
| `Z` pole mass | `91.18797807794321 GeV` | Ready comparison on the target-free D10 public row | LEP legacy, LHC electroweak fits, future `e+e-` Z-pole programs |
| `Z` frozen validation sidecar | `91.18797809193725 GeV` | Compare-only sidecar | Same scheme caveat as the `W` sidecar |
| Higgs boson mass | `125.1995304097179 GeV` | Ready comparison on the declared D10/D11 split surface | ATLAS/CMS Higgs combinations and future Higgs factories |
| Top coordinate on the D11/quark surface | `172.3523553288312 GeV` | Ready comparison only after mass-scheme matching | LHC top mass combinations and cross-section mass extractions |

The sharp CERN tests are therefore not only whether the central values agree,
but whether improved electroweak, Higgs, and top determinations converge toward
the OPH surface under the same pole or scheme conventions.

## Neutrino And Flavor Rows

| Observable | OPH value | Status | Verification route |
| --- | ---: | --- | --- |
| `m_nu_e` | `0.017454720257976796 eV` | Ready comparison on the weighted-cycle branch | Oscillation plus absolute-scale programs |
| `m_nu_mu` | `0.01948199 eV` | Ready comparison on the weighted-cycle branch | Oscillation plus absolute-scale programs |
| `m_nu_tau` | `0.05307522 eV` | Ready comparison on the weighted-cycle branch | Oscillation plus absolute-scale programs |
| Majorana phase `alpha_21` | `153.618518 deg` | Ready comparison on the declared neutrino branch | Neutrinoless double-beta and global neutrino fits |
| Majorana phase `alpha_31` | `257.003241 deg` | Ready comparison on the declared neutrino branch | Neutrinoless double-beta and global neutrino fits |

Charged-lepton absolute masses and hadron masses are not OPH predictions yet.
Those lanes still have declared derivation gaps.

## Certificate Status

The current code provides:

- `code/P_derivation/fixed_point_witness.py`: numerical fixed-point witness with
  any external inverse-alpha value accepted only as explicit compare-only
  metadata.
- `code/P_derivation/fixed_point_certificate.py`: local numerical contraction
  certificate for the implemented alpha map.

The remaining hardening step is a formal interval-arithmetic certificate for
the full D10/Thomson map, including the quadrature remainder and the final
zero-momentum transport bridge.
