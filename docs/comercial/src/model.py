# © 2026 Martín Viera. Todos los derechos reservados.
# Software propietario. Ver LICENSE — prohibida su redistribución.
"""Modelo financiero MV Data Governance — 3 escenarios x con/sin inversion redes.
Todos los montos en USD. Supuestos EDITABLES arriba; nada inventado como 'dato'.
Modelo services-led (wedge: implementar cobranza + gobernanza sobre la BD/ERP
de cada empresa) + software recurrente (Professional US$390/mes real del repo).
"""
import json

HORIZONS = [1, 3, 6, 12, 18]
MONTHS = 18

# --- Supuestos por escenario (editables) ---
# fee = proyecto de implementacion (una vez). Anclado en tarifa consultoria UY
# ~US$600/dia x 2-3 semanas (index.dev/CUTI): ~US$5k base. attach = % de
# clientes que ademas toman Professional US$390/mes.
P = {
    "pesimista": dict(r0=0.3, r1=0.8, fee=3000, attach=0.35, adds_rate=0.5, adds_r1=1.2),
    "base":      dict(r0=0.5, r1=1.5, fee=5000, attach=0.50, adds_rate=1.0, adds_r1=2.5),
    "optimista": dict(r0=0.8, r1=2.2, fee=8000, attach=0.65, adds_rate=1.5, adds_r1=4.0),
}
PRO = 390.0          # suscripcion Professional mensual (real, del repo)
CHURN = 0.03         # baja mensual sobre la base recurrente
FIXED = 30.0         # infra+dominio+herramientas por mes
PAYFEE = 0.05        # comision MercadoPago ~5%
TAX = 0.20           # impuesto efectivo sobre ganancia mensual positiva (IRAE/IRPF simplif.)
AD_COST = 400.0      # inversion mensual en redes (franja validacion US$300-500)
HIRE_COST = 4500.0   # costo empleador all-in de 1 implementador MID en UY
                     # (bruto ~US$3.4k + BPS ~13% + aguinaldo/vacacional; CUTI/BPS)


def ramp(r0, r1, m):
    return r0 + (r1 - r0) * (m - 1) / (MONTHS - 1)


def run(scenario, with_ads, hire_month=None):
    p = P[scenario]
    r0 = p["adds_rate"] if with_ads else p["r0"]
    r1 = p["adds_r1"] if with_ads else p["r1"]
    recurring_base = 0.0     # US$/mes de suscripciones vivas
    rows = []
    cum_net = 0.0
    for m in range(1, MONTHS + 1):
        new_clients = ramp(r0, r1, m)
        # ingresos del mes
        project_rev = new_clients * p["fee"]
        # nuevas suscripciones (attach) entran a la base recurrente
        recurring_base = recurring_base * (1 - CHURN) + new_clients * p["attach"] * PRO
        revenue = project_rev + recurring_base
        # costos
        var_cost = revenue * PAYFEE + FIXED
        ads = AD_COST if with_ads else 0.0
        hire = HIRE_COST if (hire_month is not None and m >= hire_month) else 0.0
        gross = revenue - var_cost - ads - hire
        tax = TAX * gross if gross > 0 else 0.0
        net = gross - tax
        cum_net += net
        rows.append(dict(m=m, new=round(new_clients, 2),
                         revenue=round(revenue), recurring=round(recurring_base),
                         net=round(net), cum=round(cum_net)))
    return rows


def summarize():
    out = {}
    for sc in P:
        out[sc] = {}
        for ads in (False, True):
            rows = run(sc, ads)
            key = "con" if ads else "sin"
            out[sc][key] = {
                "monthly_net": {h: rows[h-1]["net"] for h in HORIZONS},
                "cum_net": {h: rows[h-1]["cum"] for h in HORIZONS},
                "recurring": {h: rows[h-1]["recurring"] for h in HORIZONS},
                "series_cum": [r["cum"] for r in rows],
                "series_net": [r["net"] for r in rows],
                "clients_18m": round(sum(r["new"] for r in rows), 1),
            }
    return out


if __name__ == "__main__":
    s = summarize()
    print(json.dumps(s, indent=1, ensure_ascii=False))
    print("\n=== Tabla cumulativa neta (USD) por escenario/horizonte ===")
    print(f"{'escenario':11} {'redes':4} " + " ".join(f"{h:>8}m" for h in HORIZONS))
    for sc in P:
        for ads in ("sin", "con"):
            c = s[sc][ads]["cum_net"]
            print(f"{sc:11} {ads:4} " + " ".join(f"{c[h]:>9,}" for h in HORIZONS))
    print("\n=== Suscripciones vivas (US$/mes recurrente) a 18m ===")
    for sc in P:
        for ads in ("sin", "con"):
            print(f"{sc:11} {ads:4} recurring@18m = {s[sc][ads]['recurring'][18]:,}  ·  clientes 18m = {s[sc][ads]['clients_18m']}")
