{ lib, stdenvNoCC, fetchurl, bitsnpicas, python3 }:

stdenvNoCC.mkDerivation {
  pname = "misc-fixed-ttf";
  version = "1.1.3";

  src = fetchurl {
    url = "https://xorg.freedesktop.org/releases/individual/font/font-misc-misc-1.1.3.tar.xz";
    hash = "sha256-eavjYfWLshren1ZYmOSGMAzhzGIdUoW+wm4Utqhhj+0=";
  };

  nativeBuildInputs = [ bitsnpicas (python3.withPackages (p: [ p.fonttools ])) ];
  dontConfigure = true;

  buildPhase = ''
    runHook preBuild
    export HOME="$TMPDIR"
    mkdir converted
    for cell in 6x13 7x13 7x14 8x13 9x15 9x18 10x20; do
      for suffix in "" B O; do
        bdf="$cell$suffix.bdf"
        test -f "$bdf" || continue
        case "$suffix" in
          B) style=Bold ;;
          O) style=Oblique ;;
          *) style=Regular ;;
        esac
        # The converter invents a suffixed filename rather than overwriting.
        rm -f raw.ttf
        bitsnpicas convertbitmap -f ttf -o raw.ttf "$bdf"
        python ${./rename.py} raw.ttf "converted/MiscFixed-$cell-$style.ttf" "Misc Fixed $cell" "$style"
        python ${./verify-font.py} "$bdf" "converted/MiscFixed-$cell-$style.ttf" "Misc Fixed $cell" "$style"
      done
    done
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    install -Dm644 converted/*.ttf -t "$out/share/fonts/truetype"
    install -Dm644 COPYING "$out/share/doc/misc-fixed-ttf/COPYING"
    runHook postInstall
  '';

  meta = {
    description = "X.Org misc-fixed bitmap fonts converted to monospaced pixel-outline TrueType";
    homepage = "https://www.cl.cam.ac.uk/~mgk25/ucs-fonts.html";
    license = lib.licenses.publicDomain;
    platforms = lib.platforms.all;
  };
}
