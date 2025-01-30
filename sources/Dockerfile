# Use a FontForge base image
FROM nfqlt/fontforge:latest

# Start of Selection
# Install Node.js, npm, and other required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ttfautohint \
    python3-pip \
    python3-fontforge \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Install Python dependencies
RUN pip3 --version

RUN pip3 install --no-cache-dir "fontbakery[googlefonts]" --break-system-packages

# Set the working directory
WORKDIR /app

# Default command to keep the container ready for action
CMD ["bash"]
