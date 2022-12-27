FROM debian:buster-slim@sha256:0283b763c21691070dc9c43e918ddeedb6ab1b6b2d231cc22e9b28e636a65738

# Deps to build iosevka, from https://github.com/avivace/iosevka-docker/blob/0c1c4a9c7248398218a82c1e2f0b91a6b6912987/Dockerfile
ARG OTFCC_VER=0.10.4
ARG PREMAKE_VER=5.0.0-alpha15
ARG NODE_VER=14
RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
  build-essential \
  jq \
  file \
  curl \
  ca-certificates \
  ttfautohint \
  && curl -sSL https://deb.nodesource.com/setup_${NODE_VER}.x | bash - \
  && apt-get install -y nodejs \
  && cd /tmp \
  && curl -sSLo premake5.tar.gz https://github.com/premake/premake-core/releases/download/v${PREMAKE_VER}/premake-${PREMAKE_VER}-linux.tar.gz \
  && tar xvf premake5.tar.gz \
  && mv premake5 /usr/local/bin/premake5 \
  && rm premake5.tar.gz \
  && curl -sSLo otfcc.tar.gz https://github.com/caryll/otfcc/archive/v${OTFCC_VER}.tar.gz \
  && tar xvf otfcc.tar.gz \
  && mv otfcc-${OTFCC_VER} otfcc \
  && cd /tmp/otfcc \
  && premake5 gmake \
  && cd build/gmake \
  && make config=release_x64 \
  && cd /tmp/otfcc/bin/release-x64 \
  && mv otfccbuild /usr/local/bin/otfccbuild \
  && mv otfccdump /usr/local/bin/otfccdump \
  && cd /tmp \
  && rm -rf otfcc/ otfcc.tar.gz \
  && rm -rf /var/lib/apt/lists/*

# Install fontforge, used to modify the generated font files
RUN apt-get update && \
  apt-get install software-properties-common -y && \
  add-apt-repository ppa:fontforge/fontforge -y && \
  apt-get update && \
  apt-get install fontforge -y

CMD ["bash"]
