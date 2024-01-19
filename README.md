# Paper state checker
> **⚠ This project is not actively maintained but I might accept pull requests**

Scrape track your submission link and send updates via email

## How to run
> Required dependencies: python, pip, firefox, geckodriver

After installing the required dependencies do:
```bash
python main.py -c config.ini --notify
```

## Deploy in a Docker container
#### Configure the application
Fill in `config.ini` with the appropriate data

#### Build the container image
```bash
docker build -t paper_state_checker .
```

#### Run the container
> This might require **superuser priviliges**
```bash
docker run -d --name paper_bot --restart=always paper_state_checker:latest
```

#### To modify the configuration on the running container
```bash
docker exec -it paper_bot nano /app/config.ini
```

#### To check the application logs use
```bash
docker logs paper_bot
```