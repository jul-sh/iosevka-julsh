# Use a FontForge base image
FROM nfqlt/fontforge:latest

# Install Node.js, npm, and other required dependencies
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

RUN apt-get update && apt-get install -y python3-fontforge && apt-get install -y python3-fonttools && apt-get clean

# Set the working directory
WORKDIR /app

# Default command to keep the container ready for action
CMD ["bash"]
