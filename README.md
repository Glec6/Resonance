# DeCast-S4

Flycast (Dreamcast / Naomi / Atomiswave emulator) for jailbroken PS4 homebrew, built in WSL Ubuntu
with the DolphinPS4 / Crema PS4 toolchain (clang 21 + libc++ 21 on OpenOrbis).

- Graphics: Flycast's Vulkan renderer on DolphinPS4's RADV/GNM port, presented through VideoOut
- CPU: Flycast's x86-64 SH4 and ARM7 dynarecs, RWX code near the eboot
- Memory: fast memory over PS4 direct memory with aliasing (16 KiB pages)
- Input: DualShock 4 (ScePad), one per signed-in user; touchpad click opens the menu
- Audio: sceAudioOut, 44.1 kHz resampled to 48 kHz

## On the console

| Path | What |
|---|---|
| `/data/DeCast-S4/games` | games (GDI, CHD, CDI, ...) |
| `/data/DeCast-S4/data` | `dc_boot.bin`, `dc_flash.bin` (optional: Flycast's HLE BIOS works without), VMUs, save states, `flycast.log` |
| `/data/DeCast-S4` | `emu.cfg`, `boot-trace.log`, `crash.log` |

Title ID `DCST00001`. Install the pkg with GoldHEN's Package Installer.

## Building

```
scripts/clone-flycast.sh          # upstream Flycast at patches/BASE.txt into ~/decast-build/src
git -C ~/decast-build/src/flycast checkout -b ps4 && git apply patches/flycast-ps4.patch
scripts/seed-build-tree.sh        # sysroot + RADV build copied from Crema's build tree
scripts/rebuild-flycast.sh        # configure + build (logs in ~/decast-build/logs)
DECAST_VERSION=01.00 scripts/package-decast.sh [upload]
```

Run the scripts from WSL through `~/decast` (the space in "PS4 Projects" breaks linker flags).
