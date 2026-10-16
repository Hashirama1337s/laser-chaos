# Rigorous path alone

In plain words: `check_nohelper.cpp` is `proof/check_laser.cpp` with one line changed, so the
non-rigorous double-precision early-exit test always says "no definite failure". Only the interval computation can then
reject. Run with 64 pieces and depth 40 on four negative-control designs from `../`, it rejects every one
(`run_*.log`, last line NOT VERIFIED). Run by the referee seat; not part of `reproduce.sh`.
