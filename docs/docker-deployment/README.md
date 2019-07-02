## Requirements
To run the provided dockerized example, the following needs to be installed:
- docker

## Instructions
To run the provided dockerized example, the following commands need to be executed form the `Flask-MonitoringDashboard` folder:
- `docker-compose -f docs/docker-deployment/docker-compose.yml build`
- `docker-compose -f docs/docker-deployment/docker-compose.yml up`

The two instances of the Flask Monitoring Dashboard can then be accessed from `localhost` on ports `8080` and `8081` (as configured in `docker-compose.yml`, `nginx.conf` and `main.py`)