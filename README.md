# bm-tg-profiler

Replace all existing BM static and dynamic groups with the new set of static groups.

## Requirements
- Python 3.8 or higher
- `pip` for dependency management

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/bm-tg-profiler.git
   cd bm-tg-profiler
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the script:
   ```bash
   python main.py
   ```

2. Follow the on-screen instructions to manage static group profiles:
   ```
   usage: bm_profile.py [-h] --device_id DEVICE_ID --token TOKEN --profile_file PROFILE_FILE
   ```

3. Example profile file:
   ```json
   {
    "static_groups": [ 260, 26013 ]
   }
   ```

4. Example run:
   ```bash
      ❯ venv/bin/python bm_profile.py --token xxx --device_id 123 --profile_file ./example_profile.json
      Successfully deleted static group {'talkgroup': '2609', 'slot': '0', 'repeaterid': '123'}.
      Successfully dropped all dynamic groups.
      Successfully dropped the current call.
      Successfully added static group 260.
      Successfully added static group 26013.
   ```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.