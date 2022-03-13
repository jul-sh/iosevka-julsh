curl --location --output iosevka.zip http://github.com/be5invis/Iosevka/archive/master.zip
unzip -o iosevka
rm iosevka.zip
cp ./private-build-plans.toml ./Iosevka-master
cd Iosevka-master
npm ci
npm run build -- ttf::iosevka-julsh
npm run build -- ttf::iosevka-julsh-mono
npm run build -- ttf::iosevka-julsh-curly
npm run build -- ttf::iosevka-julsh-curly-mono
cd ../
