{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.fontforge
    pkgs.ttfautohint
    pkgs.nodejs
    pkgs.python3
    pkgs.python3Packages.fontbakery
  ];
  
  shellHook = ''
    echo "Font development shell"
    echo "Python version: $(python3 --version)"
  '';
}
