{
  description = "Font development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            fontforge
            ttfautohint
            nodejs
            python3
            python3Packages.fontbakery
          ];

          shellHook = ''
            echo "Font development shell"
            echo "Python version: $(python3 --version)"
          '';
        };
      });
}
