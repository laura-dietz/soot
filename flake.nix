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
        apps.soot-server = flake-utils.lib.mkApp { drv = packages.soot; exePath = "/bin/soot-server"; };
        defaultApp = apps.soot-server;
      }
    ) // {
      nixosModules.soot = let port = 6600; in {
        services.nginx.virtualHosts."soot.smart-cactus.org" = {
          locations."/".proxyPass = "http://localhost:${toString port}";
        };

        systemd.services.soot = {
          description = "Soot server";
          script = "${self.packages.x86_64-linux.soot}/bin/soot-server";
          environment = {
            "PYTHON_KEYRING_BACKEND" = "keyring.backends.null.Keyring";
          };
        };
      };
    };
}
