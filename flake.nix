{
  inputs = {
    artiq.url = "git+https://github.com/m-labs/artiq.git?ref=release-8&rev=431c415423e709178263d3463f8c4ab905e9b796";
    nixpkgs.follows = "artiq/nixpkgs";
  };

  outputs = { self, artiq, nixpkgs }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      # Combine attribute sets for convenience
      artiq-full = artiq.packages.x86_64-linux;

      makeArtiqBoardPackage = variant: artiq.makeArtiqBoardPackage {
        target = "kasli";
        variant = variant;
        buildCommand = 
          "python -m artiq.gateware.targets.kasli ${./firmware}/${variant}.json";
      };

      makeVariantDDB = variant: pkgs.runCommand "ddb-${variant}"  
      {
        buildInputs = artiq.devShells.x86_64-linux.boards.buildInputs;
      }
      ''
      mkdir -p $out
      artiq_ddb_template ${./firmware}/${variant}.json -o $out/device_db.py
      '';

      makeRtioMap = variant: pkgs.runCommand "rtiomap-${variant}"
      {
        buildInputs = artiq.devShells.x86_64-linux.boards.buildInputs;
      }
      ''
      mkdir -p $out
      artiq_rtiomap --device-db ${makeVariantDDB variant}/device_db.py $out/rtio_map
      '';

      makeStorage = variant: pkgs.runCommand "storage-${variant}"
      {
        buildInputs = artiq.devShells.x86_64-linux.boards.buildInputs;
      }
      ''
      mkdir -p $out
      artiq_mkfs -s ip 192.168.1.70 -f device_map ${makeRtioMap variant}/rtio_map $out/storage.img
      '';

      flash = variant: pkgs.writeShellApplication {
        name = "flash";
        runtimeInputs = artiq.devShells.x86_64-linux.boards.buildInputs;
        text = ''
          artiq_flash \
            -t kasli \
            -d ${makeArtiqBoardPackage variant} \
            -f ${makeStorage variant}/storage.img \
            erase gateware bootloader firmware storage start
        '';
  };
    in rec
    {
      apps.x86_64-linux.flash-oshqe-v1 = {
        type = "app";
        program = "${flash "oshqe-v1"}/bin/flash";
      };

      # Default shell for `nix develop`
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = [
          # Python packages
          (pkgs.python3.withPackages (ps: [
            # From the artiq flake
            artiq-full.artiq
            artiq-full.misoc
            ps.pillow
          ]))
          # Non-Python packages
          pkgs.hdfview
          artiq-full.openocd-bscanspi # needed for flashing boards, also provides proxy bitstreams
        ];
      };
      packages.x86_64-linux.default = pkgs.buildEnv{
        name="oshqe";
        paths = devShells.x86_64-linux.default.buildInputs;
      };
      packages.x86_64-linux = {
        firmware-oshqe-v1 = makeArtiqBoardPackage "oshqe-v1";
        ddb-oshqe-v1 = makeVariantDDB "oshqe-v1";
      };
    };

  # Settings to enable substitution from the M-Labs servers (avoiding local builds)
  nixConfig = {
    extra-trusted-public-keys = [
      "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc="
    ];
    extra-substituters = [ "https://nixbld.m-labs.hk" ];
    sandbox = false;
  };
}
