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

4. Example run:
   ```bash
   $ venv/bin/python bm_profile.py --token xxx --device_id 123 --profile_file ./example_profile.json
   2025-04-26 14:27:37,567 - bm-tg-profiler - INFO - Deleting 1 static groups.
   2025-04-26 14:27:38,169 - bm-tg-profiler - INFO - Deleted static group 260 on slot 0.
   2025-04-26 14:27:38,535 - bm-tg-profiler - INFO - Successfully dropped all dynamic groups.
   2025-04-26 14:27:38,904 - bm-tg-profiler - INFO - Successfully dropped the current call.
   2025-04-26 14:27:39,866 - bm-tg-profiler - INFO - Added static group 260 to slot 0.
   2025-04-26 14:27:40,831 - bm-tg-profiler - INFO - Added static group 260014 to slot 0.
   2025-04-26 14:27:41,841 - bm-tg-profiler - INFO - Added static group 260019 to slot 0.
   2025-04-26 14:27:42,829 - bm-tg-profiler - INFO - Added static group 26013 to slot 0.
   2025-04-26 14:27:43,863 - bm-tg-profiler - INFO - Added static group 26077 to slot 0.
   2025-04-26 14:27:44,894 - bm-tg-profiler - INFO - Added static group 2609 to slot 0.
   2025-04-26 14:27:45,902 - bm-tg-profiler - INFO - Added static group 26094 to slot 0.

   ```

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.