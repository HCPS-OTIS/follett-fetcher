{
  pkgs ? import <nixpkgs> { },
}:

pkgs.mkShell {
  packages = with pkgs; [
    python313Packages.requests
    python313Packages.mysql-connector
  ];
}
