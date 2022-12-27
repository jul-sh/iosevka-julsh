docker build -t iosevka-julsh --platform linux/x86_64 .
docker run -it --volume=$PWD:/workspace --workdir=/workspace --network=host --platform linux/x86_64 iosevka-julsh

