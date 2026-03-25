"""Buildozer entrypoint — imports and launches SeedApp."""

from __future__ import annotations

import importlib
app_module = importlib.import_module("Seed-Obfuscator-Android")

if __name__ == "__main__":
    app_module.SeedApp().run()
