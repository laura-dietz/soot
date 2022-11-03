{ nixpkgs ? (import <nixpkgs> {}) }:

with nixpkgs;

let
  pythonPackages = python38Packages;

  mastodonPy = pythonPackages.buildPythonPackage {
    pname = "mastodon";
    version = "1.5.0";
    buildInputs = with pythonPackages; [
      pytest-runner
    ];
    propagatedBuildInputs = with pythonPackages; [
      requests dateutil decorator pytz
      blurhash
      python-magic
    ];
    doCheck = false;
    src = fetchFromGitHub {
      owner = "halcy";
      repo = "Mastodon.py";
      rev = "89a6bd2baca4e651440402773393c19f74ee0993";
      sha256 = "sha256-A+Yp62VRrI7sBJSEOT7YEqLtxsbndRBVGpxvqbgNHgk=";
    };
  };

  soot = pythonPackages.buildPythonPackage {
    pname = "soot";
    version = "0.1.0";
    propagatedBuildInputs = with pythonPackages; [
      flask mastodonPy keyring
    ];
    src = ./.;
  };
in
  soot
