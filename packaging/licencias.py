"""
MV Data Governance · Emisión de licencias (herramienta del dueño del producto).

NO se distribuye al cliente: acá vive la clave privada que firma las licencias.

Uso
---
1) Generar el par de claves (una sola vez):

       python packaging/licencias.py keygen

   Imprime la clave pública (va en mvdg/licensing.py) y la privada (va como
   variable de entorno LICENSE_PRIVATE_KEY en Vercel). La privada NO se
   commitea ni se guarda en el repo.

2) Firmar una licencia a mano — para un cliente que pagó por transferencia,
   una licencia de prueba, o reemitir una perdida:

       python packaging/licencias.py firmar --plan professional \\
              --email cliente@empresa.com --dias 365

   Con --dias se emite con vencimiento; sin --dias, perpetua.

3) Verificar una licencia emitida (sanity check antes de mandarla):

       python packaging/licencias.py verificar --token MVDG2.xxx.yyy
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mvdg import licensing  # noqa: E402


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _keygen() -> int:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey)

    priv = Ed25519PrivateKey.generate()
    priv_raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption())
    pub_raw = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)

    print("\n" + "=" * 72)
    print("  CLAVE PÚBLICA — va en mvdg/licensing.py (se puede commitear)")
    print("=" * 72)
    print(f'\nPUBLIC_KEY_B64 = "{_b64u(pub_raw)}"\n')
    print("=" * 72)
    print("  CLAVE PRIVADA — SECRETA. Cargala como variable de entorno")
    print("  LICENSE_PRIVATE_KEY en Vercel. NO la commitees ni la compartas.")
    print("  Si se pierde, no se pueden emitir licencias nuevas (las ya")
    print("  emitidas siguen andando). Si se filtra, cualquiera puede emitir:")
    print("  hay que rotar el par y reemitir las licencias vigentes.")
    print("=" * 72)
    print(f"\n{_b64u(priv_raw)}\n")
    return 0


def _clave_privada(arg: str | None):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey)

    raw_b64 = arg or os.environ.get("LICENSE_PRIVATE_KEY", "")
    if not raw_b64:
        sys.stderr.write(
            "\n  Falta la clave privada: pasala con --clave-privada o "
            "definí LICENSE_PRIVATE_KEY.\n"
            "  Si todavía no generaste el par: python packaging/licencias.py keygen\n\n")
        raise SystemExit(2)
    pad = raw_b64 + "=" * (-len(raw_b64) % 4)
    return Ed25519PrivateKey.from_private_bytes(base64.urlsafe_b64decode(pad))


def _firmar(args) -> int:
    priv = _clave_privada(args.clave_privada)
    payload = {
        "plan": args.plan,
        "email": args.email,
        "iat": int(time.time()),
        "pid": args.pago or f"manual-{int(time.time())}",
    }
    if args.dias:
        payload["exp"] = int(time.time()) + args.dias * 86400
    body = _b64u(json.dumps(payload, ensure_ascii=False,
                            separators=(",", ":"), sort_keys=True).encode("utf-8"))
    firma = _b64u(priv.sign(body.encode("ascii")))
    token = f"MVDG2.{body}.{firma}"

    print("\n  Licencia emitida:\n")
    print(f"  {token}\n")
    print(f"  plan={payload['plan']} email={payload['email']}")
    if args.dias:
        print(f"  vence en {args.dias} días")
    else:
        print("  sin vencimiento")

    # Sanity check real: se verifica con la MISMA ruta de código que usará el
    # programa del cliente, contra la pública derivada de esta privada. Si esto
    # fallara, la licencia se mandaría rota.
    from cryptography.hazmat.primitives import serialization
    pub_b64 = _b64u(priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw))
    if licensing.verify(token, public_key_b64=pub_b64) is None:
        sys.stderr.write("\n  ERROR: la licencia emitida NO verifica.\n")
        return 1
    print("  ✓ verificada con la clave pública correspondiente")
    if pub_b64 != licensing.PUBLIC_KEY_B64:
        print("\n  AVISO: esta clave privada NO corresponde a la pública "
              "configurada\n  en mvdg/licensing.py — el programa rechazaría "
              "esta licencia.\n  Revisá que sean del mismo par.")
    return 0


def _verificar(args) -> int:
    payload = licensing.verify(args.token)
    if payload is None:
        print("\n  ✗ Licencia INVÁLIDA (firma incorrecta, vencida o mal "
              "formada)\n")
        return 1
    print("\n  ✓ Licencia válida\n")
    for k, v in sorted(payload.items()):
        print(f"    {k}: {v}")
    print()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Emisión de licencias MV Data Governance")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("keygen", help="genera el par de claves (una sola vez)")

    f = sub.add_parser("firmar", help="emite una licencia firmada")
    f.add_argument("--plan", required=True,
                   choices=[x for x in licensing.PLANES if x != licensing.PLAN_DEMO])
    f.add_argument("--email", required=True)
    f.add_argument("--dias", type=int, default=0,
                   help="vencimiento en días (0 = sin vencimiento)")
    f.add_argument("--pago", help="id de pago asociado, si lo hay")
    f.add_argument("--clave-privada", help="si no, se lee LICENSE_PRIVATE_KEY")

    v = sub.add_parser("verificar", help="verifica una licencia")
    v.add_argument("--token", required=True)

    args = p.parse_args()
    if args.cmd == "keygen":
        return _keygen()
    if args.cmd == "firmar":
        return _firmar(args)
    return _verificar(args)


if __name__ == "__main__":
    raise SystemExit(main())
