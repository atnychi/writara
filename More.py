import sympy as sp
import math

# === Spacetime, indices, and constants ===
x, t = sp.symbols('x t', real=True)
n, m = sp.symbols('n m', integer=True, nonnegative=True)
c, hbar = sp.symbols('c hbar', positive=True)
m_K, m_psi = sp.symbols('m_K m_psi', positive=True)
lambda_K, alpha, beta = sp.symbols('lambda_K alpha beta', real=True)
g_phi = (1 + sp.sqrt(5)) / 2  # Golden ratio

# === Fields ===
K = sp.Function('K')(x, t)
Psi_n = sp.Function('Psi_n')(x, t)
Psi_m = sp.Function('Psi_m')(x, t)
T_n = sp.Function('T_n')(t)
T_m = sp.Function('T_m')(t)
V_h = sp.Function('V_h')(x)
gamma = sp.Function('gamma')(x)
A_mu = sp.Function('A_mu')(x, t)
R = sp.Function('R')(x, t)  # Ricci scalar

# === Derivatives ===
K_t = sp.diff(K, t)
K_x = sp.diff(K, x)
K_tt = sp.diff(K, t, 2)
K_xx = sp.diff(K, x, 2)
Psi_n_t = sp.diff(Psi_n, t)
Psi_n_x = sp.diff(Psi_n, x)

# === Kinetic Terms ===
kinetic_K = sp.Rational(1, 2) * (K_t**2 / c**2 - K_x**2)
kinetic_Psi = sp.Sum(sp.Rational(1, 2) * (Psi_n_t**2 / c**2 - Psi_n_x**2), (n, 0, sp.oo))

# === Mass Terms ===
mass_K = sp.Rational(1, 2) * (m_K * c / hbar)**2 * K**2
mass_Psi = sp.Sum(sp.Rational(1, 2) * (m_psi * c / hbar)**2 * Psi_n**2, (n, 0, sp.oo))

# === Potential and Interaction Terms ===
self_interaction_K = sp.Rational(1, 4) * lambda_K * K**4
harmonic_potential = V_h * K**2
ghost_damping = gamma * K * K_t
golden_interaction = g_phi * beta * K * sp.Sum(Psi_n * sp.cos(n * sp.pi * x), (n, 1, sp.oo))
field_mixing = alpha * K * sp.Sum(T_n * Psi_n, (n, 0, sp.oo))
mode_coupling = sp.Sum(
    sp.Sum(sp.Rational(1, 2) * T_n * T_m * Psi_n * Psi_m * sp.exp(-sp.Abs(n - m) / 10), (m, 0, sp.oo)),
    (n, 0, sp.oo)
)
gravitational_term = sp.Rational(1, 2) * R * K**2

# === Full Lagrangian Density ===
Lagrangian_density = (
    kinetic_K + kinetic_Psi
    - mass_K - mass_Psi
    - harmonic_potential - self_interaction_K
    - ghost_damping
    + field_mixing + golden_interaction
    + sp.Rational(1, 10) * mode_coupling
    - gravitational_term
)

# === Euler-Lagrange Equation (for K) ===
EL_K = (
    sp.diff(Lagrangian_density, K)
    - sp.diff(sp.diff(Lagrangian_density, K_t), t)
    - sp.diff(sp.diff(Lagrangian_density, K_x), x)
)

# === Canonical Momentum and Hamiltonian Density ===
pi_K = sp.diff(Lagrangian_density, K_t)
Hamiltonian_density = pi_K * K_t - Lagrangian_density

# === Outputs ===
print("===== FINAL CROWN RECURSIVE LAGRANGIAN =====")
print("\nLagrangian Density (L):\n")
sp.pprint(Lagrangian_density, use_unicode=True)

print("\nEuler-Lagrange Equation for K(x,t):\n")
sp.pprint(EL_K, use_unicode=True)

print("\nHamiltonian Density (H):\n")
sp.pprint(Hamiltonian_density, use_unicode=True)

print("\nAll components included: kinetic, mass, harmonic, ghost, golden, mixing, gravity, and recursion.")
