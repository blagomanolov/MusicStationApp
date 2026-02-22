# Music Streaming Application

A modern web application for discovering and streaming radio stations from around the world. Built with FastAPI and featuring a responsive UI with Tailwind CSS.

## Features

- **Radio Station Discovery**: Browse thousands of radio stations worldwide
- **Advanced Filtering**: Filter by genre, country, or search by station name
- **Favorite Management**: Mark stations as favorites for quick access
- **Real-time Song Recognition**: Identify currently playing songs from radio streams
- **Station Playback**: Stream radio stations directly in the browser
- **Pagination**: Efficiently browse large collections of stations
- **Responsive Design**: Works seamlessly across devices

## Tech Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance ASGI framework
- **Database**: SQLite with SQLAlchemy ORM for asynchronous operations
- **Frontend**: Jinja2 templating engine with Tailwind CSS
- **API Integration**: Radio Browser API for fetching radio station data
- **Audio Streaming**: Direct streaming of radio stations with mini player
- **Deployment**: Uvicorn ASGI server

## Project Structure

```
music_app/
├── src/
│   ├── configs/
│   │   ├── config.py         # Application configuration
│   │   ├── constants.py      # Application constants
│   │   └── logging_config.py # Logging configuration
│   ├── database/
│   │   └── database.py       # Database connection and setup
│   ├── lib/
│   │   ├── crud.py           # CRUD operations
│   │   ├── models.py         # Database models
│   │   ├── populate_country.py # Country data population
│   │   ├── populate_station.py # Station data population
│   │   └── schemas.py        # Pydantic schemas
│   ├── templates/
│   │   ├── favorites.html    # Favorites page template
│   │   ├── index.html        # Main page template
│   │   ├── songs.html        # Songs library template
│   │   └── station.html      # Station playback template
│   └── main.py               # Main application entry point
├── database/
│   └── stations.db           # SQLite database file
└── requirements.txt          # Python dependencies
```

## Architecture

The application follows a clean architectural pattern with separation of concerns:

- **Presentation Layer**: HTML templates with Tailwind CSS for responsive UI
- **Application Layer**: FastAPI routes handling HTTP requests
- **Business Logic Layer**: Service handlers for station and country data
- **Data Access Layer**: SQLAlchemy ORM for database operations
- **External Services**: Radio Browser API integration

## Installation & Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd music_app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

5. Open your browser and visit `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with station listing and filtering |
| POST | `/station/create` | Create a new radio station |
| POST | `/stations/{slug}/favorite` | Toggle station as favorite |
| GET | `/favorites` | View favorite stations |
| GET | `/songs` | View song library |
| POST | `/songs/{song_id}/delete` | Delete a song |
| GET | `/stations/{slug}/play` | Play a specific station |
| GET | `/stations/{slug}/recognize` | Get current song from station |
| POST | `/songs/add` | Add a song to library |

## Functionality

### Station Discovery
Browse radio stations by genre, country, or search term. The application fetches stations from the Radio Browser API and displays them in an attractive grid layout.

### Favorite Management
Users can mark stations as favorites with a simple click, making it easy to access preferred stations later.

### Real-time Song Recognition
The application can detect the currently playing song from radio streams using ICY metadata, providing real-time information about the track.

### Audio Player
Built-in audio player with persistent mini-player that stays accessible as users navigate the site.

## Data Models

### Station
- `id`: Unique identifier
- `name`: Station name
- `genre`: Music genre
- `url`: Stream URL
- `slug`: URL-friendly identifier
- `country_code`: Associated country
- `is_favorite`: Favorite status

### Country
- `code`: Two-letter country code
- `name`: Full country name

### Song
- `id`: Unique identifier
- `name`: Song name

## 🛠️ Development Tools

The project includes a Makefile to automate common development tasks:

### Available Makefile Commands

| Command | Description |
|--------|-------------|
| `make` or `make help` | Display all available commands |
| `make venv` | Create virtual environment |
| `make install` | Install python requirements in virtual environment |
| `make run_locally` | Run app locally with auto-reload enabled |
| `make clean-venv` | Remove the virtual environment |

### Docker Commands

| Command | Description |
|--------|-------------|
| `make docker-build` | Build the docker image |
| `make docker-run` | Run the docker container |
| `make docker-stop` | Stop the docker container |
| `make docker-remove` | Remove the docker container |
| `make docker-logs` | View the logs of the running docker container |
| `make docker-shell` | Open a shell inside the docker container |
| `make docker-clean` | Stop and remove the docker container |
| `make docker-remove-image` | Remove the docker image |

### Using the Makefile

1. **Setup Development Environment:**
   ```bash
   make venv
   make install
   ```

2. **Run the Application:**
   ```bash
   make run_locally
   ```

3. **Clean Up:**
   ```bash
   make clean-venv
   ```

## Deployment

For production deployment, you can either use the traditional installation method or Docker:

### Traditional Deployment
1. Install dependencies: `make install`
2. Run the application: `make run_locally` or manually with Uvicorn

### Docker Deployment
1. Build the image: `make docker-build`
2. Run the container: `make docker-run`
3. View logs: `make docker-logs`

