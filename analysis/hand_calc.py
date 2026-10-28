"""
1D thermal-resistance cross-check for the ANSYS PV module model.

Estimates (a) the steady temperature of a healthy cell and (b) the extra
temperature rise of a single hot-spot cell, using the same geometry,
materials and boundary conditions as the FE model. Agreement within
roughly 10-15 % with the FE results is a good sanity check.
"""
import numpy as np

SIGMA = 5.670e-8          # Stefan-Boltzmann [W/m^2K^4]
T_AMB = 30.0              # ambient [C]

# Layer stack (thickness [m], conductivity [W/mK]) from the ANSYS model
FRONT = {"glass": (3.2e-3, 1.8), "EVA_1": (0.5e-3, 0.35)}
BACK = {"EVA_2": (0.5e-3, 0.35), "tedlar": (0.5e-3, 0.2)}
CELL = (0.3e-3, 148.0)

H_FRONT, H_BACK = 11.1, 5.56   # convection [W/m^2K], as in the model
EPS_FRONT, EPS_BACK = 0.84, 0.90

CELL_SIDE = 0.156              # [m]
CELL_AREA = CELL_SIDE**2
CELL_VOL = CELL_AREA * CELL[0]


def conduction_resistance(stack):
    return sum(t / k for t, k in stack.values())


def h_rad(eps, t_surf_c):
    """Linearised radiation coefficient to surroundings at ambient."""
    ts, ta = t_surf_c + 273.15, T_AMB + 273.15
    return eps * SIGMA * (ts**2 + ta**2) * (ts + ta)


def cell_temperature(q_abs, radiation=True, iters=50):
    """Steady cell temperature for absorbed heat flux q_abs [W/m^2]."""
    t = 60.0
    for _ in range(iters):
        hf = H_FRONT + (h_rad(EPS_FRONT, t) if radiation else 0.0)
        hb = H_BACK + (h_rad(EPS_BACK, t) if radiation else 0.0)
        r_f = conduction_resistance(FRONT) + 1 / hf
        r_b = conduction_resistance(BACK) + 1 / hb
        u = 1 / r_f + 1 / r_b                       # [W/m^2K]
        t = T_AMB + q_abs / u
    return t, u


def main():
    print("Conduction resistance front/back [m^2K/W]: "
          f"{conduction_resistance(FRONT):.4f} / {conduction_resistance(BACK):.4f}")

    # Heat left in the module = absorbed irradiance minus electrical output
    g, absorptance, eta = 1000.0, 0.90, 0.17
    q_abs = g * (absorptance - eta)
    print(f"\nHealthy cell, q_abs = {q_abs:.0f} W/m^2 "
          f"(G={g:.0f}, alpha={absorptance}, eta={eta})")
    for rad in (False, True):
        t, u = cell_temperature(q_abs, radiation=rad)
        print(f"  radiation={'on ' if rad else 'off'}: T_cell = {t:5.1f} C  "
              f"(U = {u:4.1f} W/m^2K)")

    # The flux actually applied in the FE model (sum of all heat-flux loads)
    q_model = 100 + 618.19 + 813.4 + 12.29
    t, _ = cell_temperature(q_model, radiation=False)
    print(f"\nFlux applied in FE model = {q_model:.0f} W/m^2 "
          f"-> T_cell = {t:.1f} C without radiation")

    # Hot spot: internal heat generation in one cell
    q_gen = 3.09e6                                  # [W/m^3] from the model
    p_hot = q_gen * CELL_VOL
    print(f"\nHot-spot cell: q''' = {q_gen:.2e} W/m^3 -> P = {p_hot:.1f} W")
    t_ok, u = cell_temperature(q_abs, radiation=True)
    # Upper bound: no lateral spreading, all extra heat leaves through the
    # cell's own footprint
    dt_upper = p_hot / (CELL_AREA * u)
    print(f"  extra rise, no lateral spreading (upper bound): {dt_upper:5.1f} K")
    # Lateral spreading through the glass widens the effective footprint;
    # spreading length L = sqrt(k_glass * t_glass / U)
    k_g, t_g = 1.8, 3.2e-3
    l_spread = np.sqrt(k_g * t_g / u)
    a_eff = (CELL_SIDE + 2 * l_spread) ** 2
    dt_spread = p_hot / (a_eff * u)
    print(f"  spreading length = {l_spread*1000:.0f} mm, "
          f"extra rise with spreading: {dt_spread:5.1f} K")
    print(f"  -> hot-spot cell approx {t_ok + dt_spread:.0f} to "
          f"{t_ok + dt_upper:.0f} C (healthy approx {t_ok:.0f} C)")

    # What the dissipation corresponds to electrically
    i_sc = 9.0
    print(f"\nP = {p_hot:.1f} W equals a reverse bias of about "
          f"{p_hot / i_sc:.1f} V at I_sc = {i_sc} A")


if __name__ == "__main__":
    main()
