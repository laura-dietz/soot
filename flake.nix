{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  inputs.mastodon-py = {
    url = "github:halcy/Mastodon.py?rev=89a6bd2baca4e651440402773393c19f74ee0993";
    flake = false;
  };

  outputs = inputs@{ self, nixpkgs, flake-utils, ... }:
    let mkSoot = { buildPythonPackage, flask, mastodonPy, keyring }:
          buildPythonPackage {
            pname = "soot";
            version = "0.1.0";
            propagatedBuildInputs = [ flask mastodonPy keyring ];
            src = ./.;
          };

        mkMastodonPy = {
          buildPythonPackage, pytest-runner, requests,
          dateutil, decorator, pytz, blurhash, python-magic
        }:
          buildPythonPackage {
            pname = "mastodon";
            version = "1.5.0";
            buildInputs = [ pytest-runner ];
            propagatedBuildInputs = [
              requests dateutil decorator pytz
              blurhash
              python-magic
            ];
            doCheck = false;
            src = inputs.mastodon-py;
          };

    in flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in rec {
        packages = flake-utils.lib.flattenTree {
          soot = pkgs.python3Packages.callPackage mkSoot { inherit (packages) mastodonPy; };
          mastodonPy = pkgs.python3Packages.callPackage mkMastodonPy {};
        };
        defaultPackage = packages.soot;
        apps.soot-server = flake-utils.lib.mkApp { drv = packages.soot; exePath = "/bin/soot-server"; };
        defaultApp = apps.soot-server;
      }
    ) // {
      nixosModules.soot = {config, ...}:
        let port = 6600;
            socket = "${config.services.uwsgi.runDir}/soot.sock";
        in {
          services.nginx.virtualHosts."soot.smart-cactus.org" = {
            locations."/".extraConfig = "uwsgi_pass unix:${socket};";
          };

          users = {
            users.soot = {
              isSystemUser = true;
              group = "soot";
              extraGroups = ["uwsgi"];
            };
            groups.soot = {
              members = ["nginx"];
            };
            users.nginx.extraGroups = ["uwsgi"];
          };

          services.uwsgi = {
            enable = true;
            plugins = ["python3"];
            instance = {
              type = "emperor";
              vassals.soot = {
                pythonPackages = pkgs:
                  let mastodonPy = pkgs.callPackage mkMastodonPy {};
                      soot = pkgs.callPackage mkSoot { inherit mastodonPy; };
                  in [soot];
                type = "normal";
                enable-threads = true;
                strict = true;
                module = "soot.server:app";
                uid = "soot";
                gid = "soot";
                chmod-socket = "660";
                inherit socket;
                env = [
                  "PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring"
                ];
              };
            };
          };
        };
      };
}
