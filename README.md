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
- **Java 17 (OpenJDK 17)**: Required for Gradle compatibility.
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

### For testing (Debug APK)
To test the app on your device without needing signing keys:
```bash
buildozer android debug deploy run
```

### For Production (Release APK)
To build a production-ready package, you must use Java 17 and provide signing credentials.

1. **Set your environment variables**:
   ```bash
   # Java 17 requirement
   export JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64
   export PATH=$JAVA_HOME/bin:$PATH

   # Signing credentials (REPLACE WITH YOUR OWN)
   export P4A_RELEASE_KEYSTORE=/path/to/your/release.jks
   export P4A_RELEASE_KEYALIAS=your_alias
   export P4A_RELEASE_KEYSTORE_PASSWD=your_password
   export P4A_RELEASE_KEYALIAS_PASSWD=your_password
   ```

2. **Build the release package**:
   ```bash
   buildozer android release
   ```

The output artifact (e.g., `seedobfuscator-1.0.0-release.apk`) will be in the `bin/` folder and is ready for installation.

## Security Warning

Always keep your secret key and the obfuscated seed separate. This tool is designed to prevent casual discovery of your seed phrase but is not a substitute for proper physical/digital security.
