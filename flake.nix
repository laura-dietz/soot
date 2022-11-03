{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  inputs.mastodon-py = {
    url = "github:halcy/Mastodon.py?rev=89a6bd2baca4e651440402773393c19f74ee0993";
    flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, mastodon-py }:
    flake-utils.lib.eachDefaultSystem (system: 
      let pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages = flake-utils.lib.flattenTree {
          soot = pkgs.python3Packages.buildPythonPackage {
            pname = "soot";
            version = "0.1.0";
            propagatedBuildInputs = with pkgs.python3Packages; [
              flask self.packages.${system}.mastodonPy keyring
            ];
            src = ./.;
          };

          mastodonPy = pkgs.python3Packages.buildPythonPackage {
            pname = "mastodon";
            version = "1.5.0";
            buildInputs = with pkgs.python3Packages; [
              pytest-runner
            ];
            propagatedBuildInputs = with pkgs.python3Packages; [
              requests dateutil decorator pytz
              blurhash
              python-magic
            ];
            doCheck = false;
            src = mastodon-py;
          };
        };
        defaultPackage = packages.soot;
        apps.soot = flake-utils.lib.mkApp { drv = packages.soot; };
        defaultApp = apps.soot;
      }
    ) // {
      nixosModules.soot = {
      };
    };
}
