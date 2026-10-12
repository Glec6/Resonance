# Resonance

Flycast (Dreamcast / Naomi / Atomiswave emulator) for jailbroken PS4 homebrew, built in WSL Ubuntu
with the DolphinPS4 / Crema PS4 toolchain (clang 21 + libc++ 21 on OpenOrbis).

- Graphics: Flycast's Vulkan renderer on DolphinPS4's RADV/GNM port, presented through VideoOut
- CPU: Flycast's x86-64 SH4 and ARM7 dynarecs, RWX code near the eboot
- Memory: fast memory over PS4 direct memory with aliasing (16 KiB pages)
- Input: DualShock 4 (ScePad), one per signed-in user; L3+R3 or a touchpad click opens the quick menu
- Menus: its own home screen (four themes, one a PS3-style XMB), settings and quick menu, in 14 languages
- Audio: sceAudioOut, 44.1 kHz resampled to 48 kHz

## On the console

| Path | What |
|---|---|
| `/data/Resonance/games` | games (GDI, CHD, CDI, ...) |
| `/data/Resonance/data` | `dc_boot.bin`, `dc_flash.bin` (optional: Flycast's HLE BIOS works without), VMUs, save states, `flycast.log` |
| `/data/Resonance` | `emu.cfg`, `boot-trace.log`, `crash.log` |

Title ID `DCST00001`. Install the pkg with GoldHEN's Package Installer.

## Building

```
scripts/clone-flycast.sh          # upstream Flycast at patches/BASE.txt into ~/resonance-build/src
git -C ~/resonance-build/src/flycast checkout -b ps4 && git apply patches/flycast-ps4.patch
scripts/seed-build-tree.sh        # sysroot + RADV build copied from Crema's build tree
scripts/rebuild-flycast.sh        # configure + build (logs in ~/resonance-build/logs)
RESONANCE_VERSION=01.00 scripts/package-resonance.sh [upload]
```

Run the scripts from WSL through `~/resonance` (the space in "PS4 Projects" breaks linker flags).
