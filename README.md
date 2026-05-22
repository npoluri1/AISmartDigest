# AISmartDigest

AI agent that watches AI shorts and extracts key intelligence from YouTube, Instagram, TikTok, and more.

## Features

- **Multi-platform support**: YouTube, Instagram, TikTok, Facebook.
- **Transcript Extraction**: Automatically extracts transcripts or page content.
- **AI-Powered Summarization**: Uses LLMs (Ollama or OpenAI) to extract AI tools, models, insights, and news.
- **Search & Stats**: Search through processed digests and view trending AI tools.
- **Browser Automation**: Uses Playwright to handle platforms that require login/cookies.

## Installation

1. **Clone the repository** (if you haven't already).
2. **Set up a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Install Playwright browsers**:
   ```powershell
   playwright install chromium
   ```
5. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your settings.
   ```powershell
   copy .env.example .env
   ```

## Usage

The application is a CLI tool. Run it using `python src/main.py` or `python -m src.main`.

### Commands

- **Process videos**:
  ```powershell
  # Single or multiple URLs
  python src/main.py process "https://www.youtube.com/watch?v=..." "https://tiktok.com/..."
  
  # Batch process from a file (one URL per line)
  python src/main.py process --file urls.txt
  ```
- **Discover new content**:
  ```powershell
  # Automatically hunt for "AI" and "VibeCoding" content across platforms
  python src/main.py discover --keyword "AI" --keyword "VibeCoding" --limit 3
  ```
- **Autonomous Monitoring (Agent Mode)**:
  ```powershell
  # Start the agent to monitor social networks in the background every hour
  python src/main.py monitor --keyword "VibeCoding" --interval 3600
  ```
- **List digests**:
  ```powershell
  python src/main.py list
  ```
- **Search digests**:
  ```powershell
  python src/main.py search "langchain"
  ```
- **Show stats**:
  ```powershell
  python src/main.py stats
  ```
- **Setup browser cookies** (for Instagram/TikTok/etc.):
  ```powershell
  python src/main.py setup-browser
  ```

## Configuration & Platforms

### API Keys
Edit the `.env` file to configure your AI provider (Ollama or OpenAI) and platform-specific keys:
- `LLM_PROVIDER`: `ollama` (default) or `openai`.
- `YOUTUBE_API_KEY`: (Optional) For more reliable YouTube metadata extraction.

### Handling Restricted Platforms (Instagram, TikTok, FB)
Some platforms require you to be logged in to view content. AISmartDigest uses browser automation for this:
1. Run `python src/main.py setup-browser`.
2. Select the platform (e.g., `instagram`).
3. A browser window will open. Log in to your account.
4. Press Enter in the CLI to save your cookies.
5. Future `process` calls for that platform will use these cookies to bypass login walls.

## Testing

### Run unit tests
```powershell
pytest tests/test_core.py
```

### Run end-to-end test (mocked)
```powershell
pytest tests/test_e2e.py
```

## Troubleshooting

- **TypeError: 'function' object is not subscriptable**: This was fixed by renaming the `list` command to `list_digests` to avoid shadowing the builtin `list` type.
- **Database Connection Error**: The `Database` class now handles `sqlite:///` prefixes correctly.
