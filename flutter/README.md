# Monteq Flutter

Native wrapper for Monteq Edge Simulator. Installable on Android/iOS/macOS/Windows/Web.

## Run
```bash
# Install Flutter: https://docs.flutter.dev/get-started/install
flutter pub get
flutter run -d chrome        # web
flutter run                  # device/emulator
flutter build web            # PWA -> build/web
flutter build apk            # Android
```

## Structure
- `lib/main.dart` — tabs: Home / Kelly / Monte / Lab / Parlay / Risk (same IA as web app)
- Math mirrors `gamble.py` + `app.html` (kelly, prob/dec parsers, fmtMoney)
- Theme: bg-black, text-zinc-100, border-zinc-800, NaN font family, rounded-none

## Web link
Full charts (Chart.js) stay in `app.html` -> `/app`. Flutter deep-links there when online.
