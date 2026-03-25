"""Seed-Obfuscator-Android: BIP-39 seed obfuscation/deobfuscation app for Android."""

import os
import hashlib

from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager


# ---------------------------------------------------------------------------
# BIP-39 logic
# ---------------------------------------------------------------------------

BIP39_PARAMS = {
    12: (128, 4),
    15: (160, 5),
    18: (192, 6),
    21: (224, 7),
    24: (256, 8),
}


def load_wordlist():
    """Load the BIP-39 wordlist from bip39.txt next to this script."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bip39.txt")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip()]
    except (OSError, UnicodeDecodeError):
        return None


def validate_seed(mnemonic, wordlist, word_to_idx):
    """Validate a BIP-39 mnemonic and return (entropy_bytes, ent_bits, cs_bits)."""
    words = mnemonic.strip().split()
    word_count = len(words)
    if word_count not in BIP39_PARAMS:
        raise ValueError(f"Error: {word_count} palabras. Use 12, 15, 18, 21 o 24.")

    ent_bits, cs_bits = BIP39_PARAMS[word_count]
    indices = []
    for i, w in enumerate(words):
        if w not in word_to_idx:
            raise ValueError(f"Palabra '{w}' (nº {i + 1}) no es BIP-39.")
        indices.append(word_to_idx[w])

    bit_string = "".join(format(idx, "011b") for idx in indices)
    entropy_bytes = int(bit_string[:ent_bits], 2).to_bytes(ent_bits // 8, "big")
    sha256_hash = hashlib.sha256(entropy_bytes).digest()
    hash_bits = bin(int.from_bytes(sha256_hash, "big"))[2:].zfill(256)

    if bit_string[ent_bits:] != hash_bits[:cs_bits]:
        raise ValueError("Checksum inválido. Verifica las palabras.")
    return entropy_bytes, ent_bits, cs_bits


def transform_seed(entropy_bytes, ent_bits, cs_bits, secret, wordlist):
    """XOR entropy with a key derived from *secret* and return new mnemonic."""
    ent_len = ent_bits // 8
    secret_bytes = secret.encode("utf-8")
    key = b""
    counter = 0
    while len(key) < ent_len:
        key += hashlib.sha256(secret_bytes + counter.to_bytes(4, "big")).digest()
        counter += 1

    new_entropy = bytes(a ^ b for a, b in zip(entropy_bytes, key[:ent_len]))
    sha256_hash = hashlib.sha256(new_entropy).digest()
    new_checksum = bin(int.from_bytes(sha256_hash, "big"))[2:].zfill(256)[:cs_bits]
    ent_bin = bin(int.from_bytes(new_entropy, "big"))[2:].zfill(ent_bits)
    full_bits = ent_bin + new_checksum
    total_words = (ent_bits + cs_bits) // 11
    return " ".join(
        wordlist[int(full_bits[i * 11 : (i + 1) * 11], 2)]
        for i in range(total_words)
    )


# ---------------------------------------------------------------------------
# UI definition (KV language)
# ---------------------------------------------------------------------------

KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<RoundedCard@MDCard>:
    radius: [dp(12)]
    elevation: 2
    padding: "16dp"
    spacing: "12dp"
    orientation: "vertical"
    adaptive_height: True
    md_bg_color: get_color_from_hex("#161B22")

MDScreen:
    md_bg_color: get_color_from_hex("#0D1117")

    MDBoxLayout:
        orientation: "vertical"
        spacing: 0

        # ── Toolbar ──────────────────────────────────────────────
        MDTopAppBar:
            title: "BIP-39 Obfuscator Pro"
            anchor_title: "center"
            elevation: 3
            md_bg_color: get_color_from_hex("#161B22")
            specific_text_color: get_color_from_hex("#E6EDF3")

        # ── Content ──────────────────────────────────────────────
        ScrollView:
            do_scroll_x: False
            bar_width: 0

            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: ["16dp", "20dp", "16dp", "32dp"]
                spacing: "16dp"

                # ── Secret key card ──────────────────────────────
                RoundedCard:
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "8dp"
                        MDIcon:
                            icon: "key-variant"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#D29922")
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "Clave de Ofuscación"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#8B949E")

                    MDTextField:
                        id: secret_input
                        hint_text: "Clave secreta"
                        password: True
                        icon_left: "shield-key"
                        mode: "fill"
                        fill_color_normal: get_color_from_hex("#21262D")
                        fill_color_focus: get_color_from_hex("#272C33")
                        hint_text_color_normal: get_color_from_hex("#8B949E")
                        text_color_normal: get_color_from_hex("#E6EDF3")
                        text_color_focus: get_color_from_hex("#E6EDF3")
                        line_color_focus: get_color_from_hex("#D29922")

                # ── Seed input card ──────────────────────────────
                RoundedCard:
                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "8dp"

                        MDIcon:
                            icon: "sprout"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#58A6FF")
                            pos_hint: {"center_y": .5}

                        MDLabel:
                            text: "Semilla de Entrada"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#8B949E")
                            size_hint_x: 1

                        MDIconButton:
                            icon: "folder-open"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#58A6FF")
                            pos_hint: {"center_y": .5}
                            on_release: app.open_file_manager()

                    MDTextField:
                        id: seed_input
                        hint_text: "Escribe o pega las palabras..."
                        multiline: True
                        mode: "fill"
                        fill_color_normal: get_color_from_hex("#21262D")
                        fill_color_focus: get_color_from_hex("#272C33")
                        hint_text_color_normal: get_color_from_hex("#8B949E")
                        text_color_normal: get_color_from_hex("#E6EDF3")
                        text_color_focus: get_color_from_hex("#E6EDF3")
                        line_color_focus: get_color_from_hex("#58A6FF")

                # ── Action buttons ───────────────────────────────
                MDBoxLayout:
                    adaptive_height: True
                    spacing: "12dp"

                    MDRaisedButton:
                        text: "OFUSCAR"
                        icon: "eye-off"
                        md_bg_color: get_color_from_hex("#9B3A2E")
                        text_color: get_color_from_hex("#FFFFFF")
                        size_hint_x: 0.5
                        elevation: 2
                        on_release: app.process_action("OFUSCAR")

                    MDRaisedButton:
                        text: "DESOFUSCAR"
                        icon: "eye"
                        md_bg_color: get_color_from_hex("#1F6FEB")
                        text_color: get_color_from_hex("#FFFFFF")
                        size_hint_x: 0.5
                        elevation: 2
                        on_release: app.process_action("DESOFUSCAR")

                # ── Result card ──────────────────────────────────
                RoundedCard:
                    md_bg_color: get_color_from_hex("#1B1500")

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "8dp"
                        MDIcon:
                            icon: "check-decagram"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#D29922")
                            pos_hint: {"center_y": .5}
                        MDLabel:
                            text: "Resultado"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: get_color_from_hex("#D29922")

                    MDTextField:
                        id: result_output
                        hint_text: "La semilla transformada aparecerá aquí"
                        readonly: True
                        multiline: True
                        mode: "fill"
                        fill_color_normal: get_color_from_hex("#241E08")
                        hint_text_color_normal: get_color_from_hex("#5A4A1A")
                        text_color_normal: get_color_from_hex("#E3B341")
                        line_color_normal: get_color_from_hex("#3D3010")

                # ── Copy button ──────────────────────────────────
                MDRaisedButton:
                    text: "   COPIAR RESULTADO"
                    icon: "content-copy"
                    md_bg_color: get_color_from_hex("#21262D")
                    text_color: get_color_from_hex("#E6EDF3")
                    pos_hint: {"center_x": .5}
                    size_hint_x: 0.7
                    elevation: 1
                    on_release: app.copy_to_clipboard()

                # ── Status bar ───────────────────────────────────
                MDLabel:
                    id: status_log
                    text: "Estado: Listo"
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: get_color_from_hex("#484F58")
                    halign: "center"
'''


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class SeedApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.wordlist = load_wordlist()
        self.word_to_idx = (
            {w: i for i, w in enumerate(self.wordlist)} if self.wordlist else {}
        )
        self.manager = MDFileManager(
            exit_manager=self.close_manager, select_path=self.select_path,
        )
        return Builder.load_string(KV)

    # --- Android lifecycle ---------------------------------------------------

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    # --- Helpers -------------------------------------------------------------

    def _show_status(self, msg, is_error=False):
        """Update the on-screen status label and show a toast."""
        self.root.ids.status_log.text = f"Estado: {msg}"
        toast(msg)

    # --- File manager --------------------------------------------------------

    def open_file_manager(self):
        path = "/sdcard" if platform == "android" else os.path.expanduser("~")
        self.manager.show(path)

    def select_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self.root.ids.seed_input.text = fh.read().strip()
            self.close_manager()
        except (OSError, UnicodeDecodeError) as exc:
            self._show_status(f"Error archivo: {exc}", is_error=True)

    def close_manager(self, *_args):
        self.manager.exit_manager()

    # --- Actions -------------------------------------------------------------

    def process_action(self, mode):
        self.root.ids.result_output.text = ""
        seed = self.root.ids.seed_input.text.strip()
        secret = self.root.ids.secret_input.text.strip()

        if not self.wordlist:
            self._show_status("Error: bip39.txt no encontrado.", is_error=True)
            return
        if not seed or not secret:
            self._show_status("Introduce clave y semilla.", is_error=True)
            return

        try:
            ent_bytes, ent_bits, cs_bits = validate_seed(
                seed, self.wordlist, self.word_to_idx,
            )
            res = transform_seed(ent_bytes, ent_bits, cs_bits, secret, self.wordlist)
            self.root.ids.result_output.text = res
            self._show_status(f"Éxito al {mode}.")
        except ValueError as ve:
            self._show_status(str(ve), is_error=True)
        except Exception as exc:
            self._show_status(f"Error: {exc}", is_error=True)

    def copy_to_clipboard(self):
        txt = self.root.ids.result_output.text
        if txt:
            Clipboard.copy(txt)
            self._show_status("Copiado al portapapeles")


if __name__ == "__main__":
    SeedApp().run()
