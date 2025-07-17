{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
      in
      with pkgs;
      {
        devShells.default = mkShell {
          buildInputs = [
            (python313.withPackages (modules: with modules; [
              pyinstaller
              pyside6
              pytest
              pythonnet
              schema
            ]))
          ];

          shellHook = ''
            echo "Setup complete."
            fish'';
        };
      }
    );
}
