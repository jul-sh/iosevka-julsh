FROM ubuntu:18.04
RUN apt-get update && \
  apt-get install software-properties-common -y && \
  add-apt-repository ppa:fontforge/fontforge -y && \
  apt-get update && \
  apt-get install fontforge -y
RUN useradd -u 1000 -m -G video julsh
USER julsh
CMD ["bash"]
