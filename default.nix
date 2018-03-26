{ nixpkgs ? (import <nixpkgs> {}) }:

with nixpkgs;

let
  pythonPackages = python36Packages;

  mastodonPy = pythonPackages.buildPythonPackage {
    pname = "mastodon";
    version = "0.1.0";
    propagatedBuildInputs = with pythonPackages; [
      requests dateutil decorator pytz
    ];
    doCheck = false;
    src = fetchFromGitHub {
      owner = "halcy";
      repo = "Mastodon.py";
      rev = "d98a3546a318bca88469a1accde99ecdf46574c1";
      sha256 = "0yl8wp58yh8p2b17g8cwb7nzdmqfr4v474lwcjd8ay0iwykfgllb";
    };
  };

  keyrings-cryptfile = pythonPackages.buildPythonPackage rec {
    pname = "keyrings.cryptfile";
    version = "1.1";
    src = fetchFromGitHub {
      owner = "frispete";
      repo = "keyrings.cryptfile";
      rev = "v${version}";
      sha256 = "52e230c8b720802d93747bc580c0a29d1fb530f3dd06f213b6a700ca9a4d0108";
    };
    buildInputs = with pythonPackages; [ pytest ];
    propagatedBuildInputs = with pythonPackages; [
      argon2_cffi keyring pycryptodome
    ];
  };

  keyrings-alt = pythonPackages.buildPythonPackage rec {
    pname = "keyrings.alt";
    version = "3.0";
    src = pythonPackages.fetchPypi {
      inherit pname version;
      sha256 = "1s1nq65sigk62idjl7n0dwkb70v36804agng2pjamgyqnzrq1b6n";

    };
    doCheck = false; # Inexplicably wants to import ctypes.windll
    buildInputs = with pythonPackages; [ pytest pycrypto ];
    propagatedBuildInputs = with pythonPackages; [
      keyring six
    ];
  };

  soot = pythonPackages.buildPythonPackage {
    pname = "soot";
    version = "0.1.0";
    propagatedBuildInputs = with pythonPackages; [
      flask mastodonPy keyring keyrings-alt
    ];
    src = ./.;
  };
in
  soot
