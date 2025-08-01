# Weather App (Docker)

A weather app running in Docker containers.

## Quick Start

1. Clone this repo:
   ```bash
   git clone git@github.com:guydevon999/weather-app.git
   cd weather-app

2. Copy the example environment file:
   cp .env.example .env

3. Start the app:
   docker-compose up -d

4. Open in your browser:
   http://localhost:5000

## Project Files

weather-app/
├── app/              # Python/Flask code
├── docker-compose.yml
├── Dockerfile
└── README.md

## Setup

   - Change ports in docker-compose.yml if needed
   - Add your API key in .env
