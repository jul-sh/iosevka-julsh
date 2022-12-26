git clone --depth 1 --branch v17.0.1 https://github.com/be5invis/Iosevka.git iosevka-repo
(cd iosevka-repo && git reset --hard 398451d7c541ae2c83425d240b4d7bc5e70e5a07)
cp ./private-build-plans.toml ./iosevka-repo
cd iosevka-repo
npm ci
npm run build -- ttf::iosevka-julsh
npm run build -- ttf::iosevka-julsh-mono
npm run build -- ttf::iosevka-julsh-curly
npm run build -- ttf::iosevka-julsh-curly-mono
cd ../
