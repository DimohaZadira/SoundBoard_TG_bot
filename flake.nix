{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, poetry2nix }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      packages.${system}.default = let
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;
      in mkPoetryApplication {
        projectDir = self;
        preferWheels = true;
      };

      devShells.${system} =
        let inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryEnv;
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              (mkPoetryEnv {
                projectDir = self;
                preferWheels = true;
              })
              poetry
            ];
          };
        };
    };
}
