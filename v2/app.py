#!/usr/bin/env python3
"""Serveur local léger pour T-AppMeteo V2 — Pêche en lac.

L'interface est également un site statique (index.html) utilisable avec
GitHub Pages ou un autre hébergement HTTPS. Lance ce serveur pour tester
l'application en local.
"""

from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


class AppMeteoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_DIR), **kwargs)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/":
            self.path = "/index.html"
        super().do_GET()

    def log_message(self, format, *args):
        # Garde les journaux lisibles pendant les essais.
        print(f"{self.address_string()} - {format % args}")


def main():
    parser = ArgumentParser(description="Lancer T-AppMeteo V2 — Pêche en lac")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute (défaut : localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Port HTTP (défaut : 8000)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), AppMeteoHandler)
    print(f"T-AppMeteo V2 disponible sur http://{args.host}:{args.port}")
    print("Arrêt : Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
