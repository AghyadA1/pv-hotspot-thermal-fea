# Thermal FEA of a PV Module with a Hot-Spot Cell Failure

**Author:** Aghyad ALI · ANSYS Mechanical 19.2 · Python

A 3D steady-state finite-element model of a 60-cell solar module, used to find out how
hot a single failed (reverse-biased) cell gets and how far its heat spreads.

![Hot-spot temperature field](figures/06_hotspot_temperature.png)

## At a glance
- **Model:** a full 1.68 m × 1.03 m module with a five-layer stack (glass / EVA / silicon /
  EVA / Tedlar) and an aluminium frame, meshed with ~1.06 M nodes (MultiZone hex), with
  convection and radiation on every face.
- **Failure case:** one cell dissipating ≈ 22.6 W, the power a cell takes when it is driven
  to ≈ 2.5 V reverse bias at I_sc ≈ 9 A.
- **Main finding:** the heat stays trapped in the failed cell. It runs ≈ 65 K hotter than a
  healthy cell, while its neighbours warm by only a few kelvin, because EVA and the gaps
  between cells conduct heat poorly. The heat flux concentrates at the cell's edges, which is
  where EVA browning and delamination would start.
- **Cross-check:** a 1D thermal-resistance model in Python
  ([`analysis/hand_calc.py`](analysis/hand_calc.py)) checks the FE temperatures.

> **Note on absolute temperatures:** the heat load applied in this version is about twice
> what a module really absorbs (see [Limitations](#limitations-and-next-steps)), so the
> absolute temperatures below are too high. The *pattern* (a hot spot confined to one
> cell, with the flux at its edges) does not depend on this.

## Why hot spots matter
When one cell in a string is shaded, cracked or mismatched, the rest of the string can
drive it into reverse bias, and it then dissipates their power as heat. Hot spots speed up
EVA browning, back-sheet delamination and glass breakage, and they are one of the most
common failures that IR inspections find in the field.

## Results
| Case | Cell temperature | Notes |
|---|---|---|
| Healthy module | max ≈ 101 °C, frame ≈ 42 °C | Cells are hottest at their centres and cooler near the frame |
| One failed cell | **max ≈ 166 °C** at the failed cell, neighbours ≈ 90–105 °C | ≈ 65 K above a healthy cell |

| Healthy module | Heat flux around the failed cell |
|---|---|
| ![Healthy module](figures/05_healthy_temperature.png) | ![Hot-spot heat flux](figures/07_hotspot_heat_flux.png) |

## Model
| Item | Value |
|---|---|
| Module | 1.68 m × 1.032 m × 31 mm, 6 × 10 cells of 156 × 156 mm |
| Layer stack (front to back) | Glass 3.2 mm / EVA 0.5 mm / Si cell 0.3 mm / EVA 0.5 mm / Tedlar 0.5 mm, aluminium frame |
| Contacts | Bonded, with perfect thermal contact between layers |
| Mesh | MultiZone hex mesh on cells, 7 mm edge sizing; ~1.06 M nodes, 173 k elements; min orthogonal quality 0.72 |
| Analysis | Steady-state thermal, MAPDL solver |

| Layer | k [W/m·K] | ρ [kg/m³] | cp [J/kg·K] |
|---|---|---|---|
| Glass | 1.8 | 3000 | 500 |
| EVA | 0.35 | 960 | 2090 |
| Silicon | 148 | 2330 | 677 |
| Tedlar | 0.2 | 1200 | 1250 |
| Aluminium | 144 (at 0 °C) | 2770 | 875 |

**Boundary conditions**
- Ambient temperature 30 °C
- Convection: h = 11.1 W/m²K on the front and sides, h = 5.56 W/m²K on the back
- Radiation to ambient: ε = 0.84 (front), 0.90 (back)
- Absorbed solar heat applied as a surface heat flux on the glass, EVA and cells
- **Failure case:** internal heat generation of 3.09 × 10⁶ W/m³ in one cell (≈ 22.6 W)

![Boundary conditions](figures/04_boundary_conditions.png)

## Analytical cross-check
[`analysis/hand_calc.py`](analysis/hand_calc.py) models the same layer stack and boundary
conditions as a 1D network of thermal resistances.

| Quantity | Hand calc | FE |
|---|---|---|
| Healthy cell, flux as applied in FE (1544 W/m²), no radiation | 126 °C | 101 °C |
| Healthy cell, realistic heat load (730 W/m²), with radiation | 56 °C | not run yet |
| Hot-spot rise above a healthy cell | 24–33 K | ≈ 65 K |

The healthy-cell result agrees in magnitude. The 1D value is higher, as expected, because it
leaves out radiation. The hot-spot rise in the FE model is about twice the 1D upper bound, and
this has not been explained yet. It is the first thing to check once the heat load is
corrected.

## Limitations and next steps
- **Heat load:** the surface fluxes add up to ≈ 1544 W/m², which is more than the
  1000 W/m² of incident sunlight. The absorbed heat should be ≈ 700–800 W/m²
  (irradiance × absorptance − electrical output). This is why the healthy module runs at
  ~100 °C, while real modules run at ~45–65 °C under similar conditions.
- **Mesh independence** has not been checked yet.
- **Steady state only.** A transient run would show how fast a hot spot develops.
- **Next:** a parametric sweep of the dissipated power (5–40 W), and a coupled
  thermal-structural run to get the stress in the glass and solder joints.

## Repository layout
```
analysis/hand_calc.py   1D analytical cross-check
figures/                Exported result images
ansys/                  Workbench project: open ansys/Solar_PV.wbpj in ANSYS 19.2+ and re-solve
                        (solver result files are not tracked because of their size)
ansys/solver_log/       MAPDL output of the hot-spot run
```

## How to run the cross-check
```
pip install -r requirements.txt
python analysis/hand_calc.py
```

## License
MIT, see [LICENSE](LICENSE). © 2025 Aghyad ALI
