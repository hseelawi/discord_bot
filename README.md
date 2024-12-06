# Discord Birthday Bot 🎂
A Discord bot that automatically sends playfully mean birthday wishes and GIFs to server members on their birthdays.

## Requirements
- Python 3.11
- Poetry 1.8.3

## Project Structure
```
.
├── birthdays.csv    # Birthday data
├── main.py         # Bot implementation
├── prompt.txt      # Claude prompt template
├── settings.py     # Configuration settings
├── poetry.lock     # Poetry dependency lock file
└── pyproject.toml  # Poetry project configuration
```

## Installation
```bash
poetry install
```

## Configuration
Create a `.env` file in the project root with the following variables:
```
DISCORD_TOKEN=your_discord_bot_token
CHANNEL_ID=your_channel_id
HEARTBEAT_CHANNEL_ID=your_heartbeat_channel_id
TENOR_API_KEY=your_tenor_api_key
TENOR_QUERY=birthday+dance    # Search query for Tenor GIFs
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
```

## Birthday Data
Create a `birthdays.csv` file with the following columns:
- `username`: Discord username
- `birthday`: Birthday in any format parseable by pandas (e.g., YYYY-MM-DD)

## Running the Bot
```bash
poetry run python main.py
```

The bot will:
1. Check for birthdays in `birthdays.csv`
2. Send a GIF and AI-generated birthday message for each celebrant
3. Automatically shut down after processing birthdays
