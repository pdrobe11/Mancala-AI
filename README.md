# Mancala AI

A mobile-friendly Streamlit companion for GamePigeon Mancala.

## Run on your computer

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (optional but recommended).
4. Install dependencies:

   `python -m pip install -r requirements.txt`

5. Start the app:

   `python -m streamlit run app.py --server.address 0.0.0.0`

6. On your iPhone, while connected to the same Wi-Fi as your computer, open:

   `http://YOUR-COMPUTER-IP:8501`

Find your computer's local IP:
- Windows: run `ipconfig` and look for the IPv4 address under your Wi-Fi adapter.
- Mac: System Settings → Wi-Fi → Details → TCP/IP.

Allow Python/Streamlit through your computer firewall if prompted.

## Current limitations

- Screenshot upload and preview are implemented.
- For this first version, enter the pit counts manually after looking at the screenshot.
- Automatic visual stone counting is not implemented yet; it needs calibration against actual GamePigeon screenshots.
- The engine assumes standard Kalah rules. Confirm that the GamePigeon variant follows these rules.
- Search depth can be increased, but deeper searches take longer.
