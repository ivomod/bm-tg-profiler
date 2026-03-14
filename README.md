# bm-tg-profiler

BrandMeister Talk Group Profile Manager — apply saved talk group presets to your DMR hotspot in one click.

---

## Disclaimer

The author takes no responsibility for any misconfiguration of DMR devices or BrandMeister account settings. **Use at your own risk.**

---

## Introduction & Rationale

**Key concepts:**

- **DMR (Digital Mobile Radio):** An open digital radio standard for professional mobile radio communications, enabling efficient voice and data transmission.
- **BrandMeister:** A global network for DMR repeaters and hotspots, providing connectivity, routing, and management of DMR talk groups.
- **Hotspot:** A small device that connects to the internet and acts as a personal DMR gateway, allowing radios to access networks like BrandMeister without a local repeater.
- **Talk Group:** A virtual channel or group ID in DMR systems that allows users to communicate with others sharing the same group, organising conversations by topic or region.

**Why this tool exists:**

Managing talk groups on a DMR hotspot — particularly in simplex mode — can be tedious, as switching between groups to avoid interference is not straightforward. The BrandMeister interface is also not optimised for quickly adding or removing large numbers of talk groups.

This project lets you define and store named **profiles** (presets) containing lists of talk groups, then apply any profile to your device in a single action. During a profile switch, all existing static groups on the target slot are removed, dynamic groups and the current call are dropped, and the connection is reset — ensuring only the new profile's groups are active.

---

## Web App

A browser-based GUI with no installation required, available at:

**https://ivomod.github.io/bm-tg-profiler/**

It runs entirely in your browser and calls the BrandMeister API directly. Your API token is stored only in your browser's `localStorage` and is never sent anywhere except `api.brandmeister.network`.

![BM TG Profiler Web App](docs/screenshot.png)

### Features

- **Connection Settings** — Configured in three guided steps:
  1. **API Token** — Enter your BrandMeister API token (stored only in your browser, never shared).
  2. **Callsign** — Enter your callsign (e.g. `SP9ZEN`).
  3. **Device ID** — Click **🔄 Fetch** to load all devices registered to your callsign. Select the target device from the dropdown.

  Settings are persisted in `localStorage` and restored on every visit. Default time slot is **Slot 0 (simplex)**.

- **Profile Manager** — Create and manage multiple named profiles, each containing a list of talk group numbers. Profiles are stored in `localStorage`.

- **One-click Apply** — Selecting a profile and clicking Apply runs the full 5-step sequence with a live progress tracker and timestamped activity log. Groups on other slots are left untouched:
  1. Delete static groups on the selected slot
  2. Drop dynamic groups
  3. Drop current call
  4. Reset connection
  5. Set new static groups

- **View Current Groups** — Inspect which static groups are active on the selected slot without applying any changes.

- **Save as Profile** — Snapshot the device's current static groups into a new named profile directly from the Current Groups panel.

- **Clear Slot** — Remove all static talk groups from the selected slot (with confirmation).

- **Import / Export** — Import talk groups from a JSON file (`{"static_groups": [...]}`). Export any single profile or all profiles at once to JSON for backup or transfer.

- **Talk group names** — Names are automatically fetched from the BrandMeister API and displayed alongside group numbers. Cached in `localStorage` for 24 hours.

- **Dark / Light mode** — Toggle in the top-right corner; preference is saved in `localStorage`.

- **Polish / English** — Language selector in the top-right corner; preference is saved in `localStorage`.

### Usage

1. Open **https://ivomod.github.io/bm-tg-profiler/** in your browser.
2. Enter your **Callsign**, **API Token**, and **Time Slot** in the Connection Settings panel.
3. Click **🔄 Fetch** to load your BrandMeister devices — select the target from the dropdown.
4. Click **Save Settings**.
5. Create a profile with **+ New** in the Profiles panel and add talk group numbers.
6. Click **▶ Apply** next to a profile (or select it and click **Apply Profile**) to push it to your device.

### Source

The web app lives in `webapp/`:

```
webapp/
├── index.html   # HTML structure
├── styles.css   # All styles
├── i18n.js      # English and Polish translations
└── app.js       # Application logic
```

---

## CLI

A Python command-line tool for applying profiles from a terminal or scripts. Lives in `cli/`.

### Requirements

- Python 3.8 or higher
- `pip` for dependency management
- BrandMeister API token — see [Introducing User API keys](https://news.brandmeister.network/introducing-user-api-keys/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ivomod/bm-tg-profiler.git
   cd bm-tg-profiler/cli
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

```bash
python bm_profile.py --help
```

```
usage: bm_profile.py [-h] --device_id DEVICE_ID --token TOKEN [--slot SLOT] --profile_file PROFILE_FILE [--plain-print]

Manage static groups for BrandMeister.

options:
  -h, --help                    show this help message and exit
  --device_id DEVICE_ID         The device ID of the repeater.
  --token TOKEN                 The BrandMeister API token.
  --slot SLOT                   The time slot to use (default: 0).
  --profile_file PROFILE_FILE   Path to the JSON profile file containing static groups.
  --plain-print                 Disable colours and emojis in output.
```

### Profile file format

```json
{
  "static_groups": [
    260,
    260014,
    260019,
    26013,
    26077,
    2609,
    26094
  ]
}
```

Example profiles are included in `cli/profiles/`. Use `cli/example_profile.json` as a starting point.

### Example run

```bash
$ python bm_profile.py --token xxx --device_id 123 --profile_file ./example_profile.json
ℹ️ 📄 Loaded profile with 1 static groups
ℹ️ 🧹 Deleting 10 static groups.
ℹ️ 🗑️ Deleted static group 260014 on slot 0.
ℹ️ 🗑️ Deleted static group 26040 on slot 0.
ℹ️ 🗑️ Deleted static group 26013 on slot 0.
ℹ️ 🗑️ Deleted static group 260 on slot 0.
ℹ️ 🗑️ Deleted static group 260019 on slot 0.
ℹ️ 🗑️ Deleted static group 2609 on slot 0.
ℹ️ 🗑️ Deleted static group 2600 on slot 0.
ℹ️ 🗑️ Deleted static group 26077 on slot 0.
ℹ️ 🗑️ Deleted static group 26094 on slot 0.
ℹ️ 🗑️ Deleted static group 2603351 on slot 0.
ℹ️ ✅ All delete threads completed.
ℹ️ 🗑️ Successfully dropped all dynamic groups.
ℹ️ 📞 Successfully dropped the current call.
ℹ️ 🔄 Successfully reset connection.
ℹ️ ➕ Added static group 26013 to slot 0.
ℹ️ ✅ All add threads completed.
✨ 🎉 Profile successfully applied!
```

### Tests

```bash
cd cli
python3 -m pytest -v
```

### Source

```
cli/
├── bm_profile.py       # Main entry point
├── bm_client.py        # BrandMeister API client
├── logger.py           # Logging utilities
├── requirements.txt    # Python dependencies
├── example_profile.json
├── profiles/           # Example profile files
├── test_bm_client.py
├── test_bm_profile.py
└── test_logger.py
```

---

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.
