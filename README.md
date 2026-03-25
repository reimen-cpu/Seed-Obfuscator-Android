# Seed-Obfuscator-Android

A professional BIP-39 Seed Obfuscator for Android. This tool allows you to transform your standard recovery phrases into an obfuscated version using a secret key, providing an extra layer of security for your cold storage backups.

## Features

- **BIP-39 Validation**: Ensures your input seed follows the BIP-39 standard (checksum verification).
- **Secure XOR Transformation**: Obfuscates the entropy of your seed using a SHA-256 derived key from your secret.
- **File Manager Integration**: Easily import seed phrases from text files.
- **Production UI**: Clean, high-performance dark theme with intuitive card-based layout.
- **Android Optimized**: Handles Android lifecycle events and clipboard operations natively.

## Prerequisites

- Python 3.8+
- [Buildozer](https://github.com/kivy/buildozer) (for Android compilation)
- BIP-39 wordlist (`bip39.txt` must be in the project root)

## Installation & Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/reimen-cpu/Seed-Obfuscator-Android
   cd Seed-Obfuscator-Android
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Or install manually:
   pip install kivy==2.3.0 kivymd==1.2.0
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Compiling for Android

To build the production release APK:

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the build command**:
   ```bash
   buildozer android release
   ```

3. **Install and run on device**:
   ```bash
   buildozer android release deploy run
   ```

The output APK will be in the `bin/` folder.

## Security Warning

Always keep your secret key and the obfuscated seed separate. This tool is designed to prevent casual discovery of your seed phrase but is not a substitute for proper physical/digital security.
