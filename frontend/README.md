# Automotive Security System - Frontend

This Flutter project implements the mobile app for an automotive security system that monitors suspicious RF signals in vehicles.

## Basic Implementation Plan

- **State Management:** Provider (see `lib/providers/`)
- **Navigation:** BottomNavigationBar with Dashboard, Alerts, History, and Settings screens
- **Screens:**
  - Dashboard: Shows signal strength (placeholder)
  - Alerts: Displays alerts (placeholder)
  - History: Shows history of events (placeholder)
  - Settings: User configuration (placeholder)
- **Theming:** Light/Dark theme support
- **BLE/Wi-Fi:** Placeholder service in `lib/core/ble_wifi_service.dart`

## Getting Started

1. Run `flutter pub get` to fetch dependencies.
2. Run the app with `flutter run`.

## Next Steps

- Implement BLE/Wi-Fi communication logic
- Fill out UI screens with real data and controls
- Add persistent storage and advanced features

Refer to `IMPLEMENTATION_PLAN.md` for the full project roadmap.
