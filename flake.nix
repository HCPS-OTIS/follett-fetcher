{
  description = "Tool to periodically retrieve information from Follett Destiny";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    {

      nixosModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        with lib;

        {

          options.services.follett-fetcher = {
            enable = mkEnableOption "Enable the follett-fetcher";
            log_level = mkOption {
              type = types.int;
              default = 5;
              description = "how much messages to log in the console";
            };
          };

          config = mkIf config.services.follett-fetcher.enable {
            systemd.services.follett-fetcher = {
              description = "Follett API scraper";
              wantedBy = [ "networking.target" ];
              after = [ "networking.service" ];
              environment = {
                EXAMPLE_LOG_LEVEL = builtins.toString follett-fetcher.log_level;
              };
              serviceConfig = {
                Type = "simple";
                ExecStart = "${self.packages.${pkgs.system}.default}/bin/follett-fetcher";
                Restart = "on-failure";
                ProtectHome = "read-only";
              };
            };
          };

        };

    };
}
