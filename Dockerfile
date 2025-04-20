# Use a base image that includes Python 3.12.2
FROM python:3.12.2-slim

LABEL       author="Omar Sanchez (OsanchezDev)" maintainer="OsanchezDev@gmail.com"
LABEL       org.opencontainers.image.source="https://github.com/OsanchezDev"
LABEL       org.opencontainers.image.licenses=MIT

# Prevent interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    fonts-liberation \
    iproute2 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Add Tini
ENV TINI_VERSION="v0.19.0"
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

# Set environment variables to avoid Chrome sandbox issues
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="/root/.local/bin:$PATH"

# Setup user and working directory
RUN         useradd -m -d /home/container -s /bin/bash container
USER        container
ENV         USER=container HOME=/home/container
WORKDIR     /home/container

## Copy over entrypoint.sh and set permissions
COPY        --chown=container:container . /home/container
RUN         chmod +x /home/container/entrypoint.sh

# Use tini to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "-g", "--"]
CMD         ["/entrypoint.sh"]
