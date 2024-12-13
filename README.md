# Discord Birthday Bot 🎂
A Discord bot that automatically sends playfully mean birthday wishes and GIFs to server members on their birthdays.

## Requirements
- Python 3.11
- Poetry 1.8.3

## Project Structure
```
.
├── main.py         # Bot implementation
├── prompt.txt      # Claude prompt template
├── settings.py     # Configuration settings
├── poetry.lock     # Poetry dependency lock file
└── pyproject.toml  # Poetry project configuration
```

## Installation
```bash
poetry install --no-root
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
DATA_PATH=path_to_birthdays_data    # Local file path or S3 URI to birthday csv (see section below)
```

## Birthday Data
The bot reads birthday data from a CSV file specified by the `DATA_PATH` environment variable. The file can be stored locally or in an S3 bucket. The CSV should have the following structure:

```csv
username,birthday
user123,1990-01-15
johndoe,1995-07-30
```

The columns are:
- `username`: Discord username
- `birthday`: Birthday in YYYY-MM-DD format

## Running the Bot
```bash
poetry run python main.py
```

The bot will:
1. Check for birthdays in the configured data source
2. Send a GIF and AI-generated birthday message for each celebrant
3. Automatically shut down after processing birthdays
