FROM archlinux
LABEL maintainer="Ricard Lado <ricard@lado.one>"
LABEL repository="https://github.com/RLado/paper_state_checker"

# Copy files
RUN mkdir /app
COPY . /app
WORKDIR /app

# Install dependencies
RUN pacman -Syy && pacman -S --noconfirm \
    python \
    python-pip \
    nano \
    firefox \
    geckodriver
RUN pip install -r requirements.txt --break-system-packages

# Run bot
ENTRYPOINT ["python", "-u", "main.py", "-c", "config.ini", "--notify"]