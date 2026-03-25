import os
import hashlib
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.filemanager import MDFileManager
from kivy.utils import platform

# --- Lógica BIP-39 ---
BIP39_PARAMS = {12: (128, 4), 15: (160, 5), 18: (192, 6), 21: (224, 7), 24: (256, 8)}

def load_wordlist():
    path = os.path.join(os.path.dirname(__file__), "bip39.txt")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return None

def validate_seed(mnemonic, wordlist, word_to_idx):
    words = mnemonic.strip().split()
    word_count = len(words)
    if word_count not in BIP39_PARAMS:
        raise ValueError(f"Error: {word_count} palabras. Use 12, 15, 18, 21 o 24.")
    
    ent_bits, cs_bits = BIP39_PARAMS[word_count]
    indices = []
    for i, w in enumerate(words):
        if w not in word_to_idx:
            raise ValueError(f"Palabra '{w}' (nº {i+1}) no es BIP-39.")
        indices.append(word_to_idx[w])
    
    bit_string = "".join(format(idx, "011b") for idx in indices)
    entropy_bytes = int(bit_string[:ent_bits], 2).to_bytes(ent_bits // 8, "big")
    sha256_hash = hashlib.sha256(entropy_bytes).digest()
    hash_bits = bin(int.from_bytes(sha256_hash, "big"))[2:].zfill(256)
    
    if bit_string[ent_bits:] != hash_bits[:cs_bits]:
        raise ValueError("Checksum inválido. Verifica las palabras.")
    return entropy_bytes, ent_bits, cs_bits

def transform_seed(entropy_bytes, ent_bits, cs_bits, secret, wordlist):
    ent_len = ent_bits // 8
    secret_bytes = secret.encode("utf-8")
    key, counter = b"", 0
    while len(key) < ent_len:
        key += hashlib.sha256(secret_bytes + counter.to_bytes(4, "big")).digest()
        counter += 1
    new_entropy_bytes = bytes(a ^ b for a, b in zip(entropy_bytes, key[:ent_len]))
    sha256_hash = hashlib.sha256(new_entropy_bytes).digest()
    new_checksum = bin(int.from_bytes(sha256_hash, "big"))[2:].zfill(256)[:cs_bits]
    ent_bin = bin(int.from_bytes(new_entropy_bytes, "big"))[2:].zfill(ent_bits)
    full_bits = ent_bin + new_checksum
    return " ".join(wordlist[int(full_bits[i*11:(i+1)*11], 2)] for i in range((ent_bits + cs_bits)//11))

# --- Interfaz KV ---
KV = '''
MDScreen:
    md_bg_color: 0.1, 0.11, 0.14, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "12dp"
        spacing: "8dp"

        MDTopAppBar:
            title: "BIP-39 Obfuscator Pro"
            anchor_title: "center"
            md_bg_color: 0.13, 0.15, 0.18, 1
            elevation: 2

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                adaptive_height: True
                padding: "10dp"
                spacing: "15dp"

                MDTextField:
                    id: secret_input
                    hint_text: "Clave Secreta"
                    password: True
                    mode: "fill"
                    fill_color_normal: 0.17, 0.19, 0.24, 1

                MDBoxLayout:
                    adaptive_height: True
                    spacing: "10dp"
                    MDLabel:
                        text: "Semilla de entrada:"
                        theme_text_color: "Hint"
                    MDIconButton:
                        icon: "file-document"
                        on_release: app.open_file_manager()

                MDTextField:
                    id: seed_input
                    hint_text: "Escribe o pega tus palabras..."
                    multiline: True
                    mode: "rectangle"

                MDBoxLayout:
                    adaptive_height: True
                    spacing: "15dp"
                    
                    MDRaisedButton:
                        text: "OFUSCAR"
                        md_bg_color: 0.8, 0.3, 0.3, 1
                        size_hint_x: 0.5
                        on_release: app.process_action("OFUSCAR")

                    MDRaisedButton:
                        text: "DESOFUSCAR"
                        md_bg_color: 0.2, 0.4, 0.8, 1
                        size_hint_x: 0.5
                        on_release: app.process_action("DESOFUSCAR")

                MDTextField:
                    id: result_output
                    hint_text: "Resultado"
                    readonly: True
                    multiline: True
                    mode: "rectangle"
                    text_color_normal: 0.2, 0.8, 0.5, 1

                MDRoundFlatIconButton:
                    icon: "content-copy"
                    text: "Copiar Resultado"
                    pos_hint: {"center_x": .5}
                    on_release: app.copy_to_clipboard()
                
                MDLabel:
                    id: status_log
                    text: "Estado: Listo"
                    theme_text_color: "Secondary"
                    font_style: "Caption"
                    halign: "center"
'''

class SeedApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.wordlist = load_wordlist()
        if self.wordlist:
            self.word_to_idx = {w: i for i, w in enumerate(self.wordlist)}
        else:
            self.word_to_idx = {}
        self.manager = MDFileManager(exit_manager=self.close_manager, select_path=self.select_path)
        return Builder.load_string(KV)

    def log_status(self, msg, is_error=False):
        # Actualizar el texto en pantalla directamente (más seguro)
        self.root.ids.status_log.text = f"Estado: {msg}"
        
        # Snackbar para versión 1.2.0 (manera ultra-segura de llamarlo)
        try:
            # En 1.2.0 a veces 'text' falla en el init, lo asignamos después
            snackbar = Snackbar()
            snackbar.text = msg
            if is_error:
                snackbar.bg_color = (0.8, 0.2, 0.2, 1)
            snackbar.open()
        except Exception as e:
            print(f"Error mostrando snackbar: {e}")

    def open_file_manager(self):
        path = "/sdcard" if platform == "android" else os.path.expanduser("~")
        self.manager.show(path)

    def select_path(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.root.ids.seed_input.text = f.read().strip()
            self.close_manager()
        except Exception as e:
            self.log_status(f"Error archivo: {str(e)}", True)

    def close_manager(self, *args):
        self.manager.exit_manager()

    def process_action(self, mode):
        self.root.ids.result_output.text = ""
        seed = self.root.ids.seed_input.text.strip()
        secret = self.root.ids.secret_input.text.strip()

        if not self.wordlist:
            self.log_status("Error: bip39.txt no encontrado.", True)
            return
        if not seed or not secret:
            self.log_status("Introduce clave y semilla.", True)
            return

        try:
            ent_bytes, ent_bits, cs_bits = validate_seed(seed, self.wordlist, self.word_to_idx)
            res = transform_seed(ent_bytes, ent_bits, cs_bits, secret, self.wordlist)
            
            self.root.ids.result_output.text = res
            self.log_status(f"Éxito al {mode}.")
        except ValueError as ve:
            self.log_status(str(ve), True)
        except Exception as e:
            self.log_status(f"Error: {str(e)}", True)

    def copy_to_clipboard(self):
        txt = self.root.ids.result_output.text
        if txt:
            Clipboard.copy(txt)
            self.log_status("Copiado al portapapeles")

if __name__ == "__main__":
    SeedApp().run()
