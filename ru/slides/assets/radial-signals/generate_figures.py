#!/usr/bin/env python3
"""Generate the numerical figures used by the radial-signals lecture."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq


OUTPUT_DIR = Path(__file__).resolve().parent

# Безразмерная задержка между двумя одинаковыми падающими геодезическими.
delta = 0.5


def F(q):
    q = np.asarray(q)
    return q**2 + 2 * q + 2 * np.log(np.abs(q - 1))


def H(q):
    q = np.asarray(q)
    return (2 / 3) * q**3 + F(q)


def q_M(tau):
    return np.cbrt(1 - 1.5 * tau)


def q_O(tau):
    return np.cbrt(1 - 1.5 * (tau - delta))


def tau_M(q):
    return (2 / 3) * (1 - q**3)


def tau_O(q):
    return delta + (2 / 3) * (1 - q**3)


def reception_q(qe):
    """Return q_r from H(q_r) = H(q_e) + delta on the physical branch."""
    target = H(qe) + delta

    if qe > 1:
        # Outside the horizon H is monotone increasing.
        lo = qe
        hi = max(qe + 0.1, 1.2 * qe)
        while H(hi) < target:
            hi *= 1.5
        return brentq(lambda q: H(q) - target, lo, hi)

    if qe < 1:
        # Inside the horizon H ranges from 0 at q=0 to -infinity at q=1-.
        if target > 0:
            return np.nan
        if abs(target) < 1e-14:
            return 0.0
        return brentq(lambda q: H(q) - target, 0.0, qe)

    return 1.0


def reception_time(tau_e):
    if abs(tau_e) < 1e-13:
        return delta
    qe = q_M(tau_e)
    qr = reception_q(qe)
    if not np.isfinite(qr):
        return np.nan
    return tau_O(qr)


def plot_schwarzschild_time():
    q0 = 2.0  # Начало рисунка: r = 4 r_g.
    qsch = np.linspace(q0, 1.00015, 900)
    rho_sch = qsch**2

    # Время Шварцшильда вдоль геодезической; начало отсчёта при q=q0.
    def t_s_raw(q):
        return -(2 / 3) * q**3 - 2 * q - np.log(np.abs((q - 1) / (q + 1)))

    t_s_elapsed = t_s_raw(qsch) - t_s_raw(q0)

    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ax.plot(t_s_elapsed, rho_sch, lw=2.2, label="падающий объект")
    ax.axhline(1, ls="--", lw=1.2, label=r"горизонт $r=r_g$")
    ax.set_xlim(left=0)
    ax.set_ylim(0.92, 4.05)
    ax.set_xlabel(r"безразмерное время Шварцшильда $c\,\Delta t_S/r_g$")
    ax.set_ylabel(r"$\rho=r/r_g$")
    ax.set_title("Падение во времени Шварцшильда")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "schwarzschild_time.png", dpi=220)
    plt.close(fig)


def plot_exact_spacetime():
    tau_min = -0.9
    tm = np.linspace(tau_min, 2 / 3 - 1e-4, 800)
    to = np.linspace(tau_min, delta + 2 / 3 - 1e-4, 900)

    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    ax.plot(q_M(tm) ** 2, tm, lw=2.2, label="объект M")
    ax.plot(q_O(to) ** 2, to, lw=2.2, label="объект O")
    ax.axvline(1, ls="--", lw=1.4, label=r"горизонт $\rho=1$")

    for te, label in [
        (-0.25, "сигнал до горизонта"),
        (0.0, "сигнал на горизонте"),
        (0.16, "сигнал после горизонта"),
    ]:
        if te == 0:
            ax.plot([1, 1], [0, delta], lw=2.0, label=label)
            continue
        qe = q_M(te)
        qr = reception_q(qe)
        qs = np.linspace(qe, qr, 300)
        taus = te + F(qs) - F(qe)
        ax.plot(qs**2, taus, lw=2.0, label=label)

    ax.scatter([1, 1], [0, delta], s=45, zorder=5)
    ax.set_xlabel(r"$\rho=r/r_g$")
    ax.set_ylabel(r"$\tau=ct/r_g$")
    ax.set_title(r"Падение и обмен световыми сигналами ($\delta=0.5$)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "exact_spacetime.png", dpi=220)
    plt.close(fig)


def plot_exact_signal_map():
    q_star = brentq(lambda q: H(q) + delta, 1e-12, 1 - 1e-12)
    tau_e_max = tau_M(q_star)
    tau_r_max = delta + 2 / 3

    te_before = np.linspace(-1.0, -2e-7, 520)
    te_after = np.linspace(2e-7, tau_e_max - 2e-5, 420)
    tr_before = np.array([reception_time(x) for x in te_before])
    tr_after = np.array([reception_time(x) for x in te_after])

    fig, (ax, zoom) = plt.subplots(
        1,
        2,
        figsize=(11.2, 5.2),
        gridspec_kw={"width_ratios": [1.42, 1]},
    )

    def draw_map(axis, show_legend=False):
        axis.plot(
            np.append(te_before, 0),
            np.append(tr_before, delta),
            lw=2.8,
            color="#2378b8",
            label="сигнал излучён снаружи",
        )
        axis.plot(
            np.insert(te_after, 0, 0),
            np.insert(tr_after, 0, delta),
            lw=2.8,
            color="#e8762c",
            label="сигнал излучён внутри",
        )
        axis.scatter(
            [0],
            [delta],
            s=78,
            color="#2ca25f",
            edgecolor="white",
            linewidth=1.0,
            zorder=6,
            label="сигнал на горизонте",
        )
        axis.axvline(0, ls=":", lw=1.2, color="#666666")
        axis.axhline(delta, ls=":", lw=1.2, color="#666666")
        axis.grid(alpha=0.25)
        if show_legend:
            axis.legend(loc="upper left", fontsize=10.5)

    draw_map(ax, show_legend=True)
    ax.scatter(
        [tau_e_max],
        [tau_r_max],
        marker="o",
        s=58,
        facecolors="white",
        edgecolors="#7b3294",
        linewidths=2.0,
        zorder=5,
    )
    ax.annotate(
        "предел у сингулярности",
        xy=(tau_e_max, tau_r_max),
        xytext=(tau_e_max - 0.52, tau_r_max - 0.18),
        fontsize=10,
        arrowprops={"arrowstyle": "->", "lw": 1.0},
    )
    ax.set_xlim(-1.05, 0.41)
    ax.set_ylim(-0.72, 1.25)
    ax.set_xlabel(r"время излучения  $\tau_e=ct_e/r_g$")
    ax.set_ylabel(r"время поглощения  $\tau_r=ct_r/r_g$")
    ax.set_title("Вся физическая область")

    draw_map(zoom)
    zoom.set_xlim(-0.12, 0.12)
    zoom.set_ylim(delta - 0.16, delta + 0.16)
    zoom.set_xlabel(r"время излучения  $\tau_e$")
    zoom.set_ylabel(r"время поглощения  $\tau_r$")
    zoom.set_title("Около горизонта")
    zoom.annotate(
        "нет скачка",
        xy=(0, delta),
        xytext=(-0.105, delta + 0.105),
        fontsize=12,
        weight="bold",
        color="#176b3a",
        arrowprops={"arrowstyle": "->", "color": "#176b3a", "lw": 1.4},
    )

    fig.suptitle(r"Время поглощения непрерывно зависит от времени излучения ($\delta=0.5$)")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "exact_signal_map.png", dpi=220)
    plt.close(fig)


def main():
    plot_schwarzschild_time()
    plot_exact_spacetime()
    plot_exact_signal_map()


if __name__ == "__main__":
    main()
