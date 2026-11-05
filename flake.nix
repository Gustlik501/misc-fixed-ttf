{
  description = "Pixel-outline TrueType conversions of X.Org misc-fixed fonts";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      packages = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in rec {
          misc-fixed-ttf = pkgs.callPackage ./package.nix { };
          default = misc-fixed-ttf;
        });
      overlays.default = final: prev: {
        misc-fixed-ttf = final.callPackage ./package.nix { };
      };
      checks = forAllSystems (system: {
        inherit (self.packages.${system}) misc-fixed-ttf;
      });
      devShells = forAllSystems (system:
        let pkgs = import nixpkgs { inherit system; };
        in { default = pkgs.mkShell {
          packages = [ pkgs.fontconfig pkgs.imagemagick pkgs.kitty
            pkgs.xorg.fontmiscmisc (pkgs.python3.withPackages (p: [ p.fonttools ])) ];
        }; });
    };
}
