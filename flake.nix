{
  description = "Herdr plugin: keep spaces sorted by title";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      # Same system list as herdr's own flake.
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      # The plugin directory (what `herdr plugin link` wants), with python3 pinned to the store:
      # plugin commands run with herdr's PATH, which on NixOS rarely contains python3.
      packages = forAll (pkgs: {
        default = pkgs.runCommand "herdr-sort-spaces" { } ''
          mkdir -p $out
          cp --no-preserve=mode ${./herdr-plugin.toml} $out/herdr-plugin.toml
          cp --no-preserve=mode ${./sort_spaces.py} $out/sort_spaces.py
          substituteInPlace $out/herdr-plugin.toml \
            --replace-fail '"python3"' '"${pkgs.python3}/bin/python3"'
        '';
      });

      checks = forAll (pkgs: {
        unit = pkgs.runCommand "herdr-sort-spaces-test" { nativeBuildInputs = [ pkgs.python3 ]; } ''
          cp ${./sort_spaces.py} sort_spaces.py
          cp ${./test_sort_spaces.py} test_sort_spaces.py
          python3 test_sort_spaces.py
          touch $out
        '';
      });
    };
}
