# Until Then (010019C023004000) bring-up

Status: survey completed on Windows; no IPA or gameplay test yet.

## Tested package

- Base: v0; update: v589824 (display version 1.0.9).
- Update `main` build ID: `53e2366a73ef1a06f185c5d80c13d642`.
- SDK 19. Both NSZ files decompressed to NSP with NCA hash verification.
- The update's RomFS manifest has 230,496 files (3,868.4 MB).
- The extracted files and `RomFS.img` are under `D:\迅雷云盘\UntilThen\extract`; game data and keys are not in this repository.

## Engine and graphics evidence

- This is a Godot build: the RomFS contains `.godot` exports, `.gdshader` resources and a `shader_cache` tree. The `main` NSO contains `Godot Engine` markers.
- The package includes `subsdk0` (NintendoSDK_OpenGL) and `subsdk1` (NintendoSDK_Vulkan), both importing `nvnBootstrapLoaderInternal`. `main` imports `nvnBootstrapLoader`, but no `vk*` or `egl*` symbols directly. Its actual renderer must be established from the startup path, rather than inferred from these strings alone.
- `shader_cache` contains 472 `.vulkan.cache` files. A sampled file begins with `GDSC` cache version 3 and a `GSBD` binary version 4. Godot 4.3's `shader_rd.cpp` and Vulkan driver source document these formats: the latter stores SPIR-V stages as Smol-V, optionally compressed again with Zstd. The sample contains no raw SPIR-V magic.
- The current `profile_guess.py` selects `main sdk` and NVN based on `main`'s import. Its raw-SPIR-V scan does not see the shaders inside Godot's cache. This is insufficient to build a working shader package for this game.

## Build-chain issue

`Flamelovers/nxkit` still pins `NXNATIVE_REF=2db12f7`, but its current Windows patches target later nxnative code. `nxkit.py setup` fails applying `0000-windows-paths.patch` at `shader_split.py:1759`. The fork needs a compatible pinned nxnative commit and a patch refresh before its one-command build can run reliably. Do not advance the pin without checking every general and game patch on both Windows and the Mac runner.

## Next work

1. Determine from the updated `main`'s startup path which renderer is selected, and which of the OpenGL/Vulkan subsdk modules it loads.
2. Add a bounded reader for Godot `GDSC`/`GSBD` cache files and decode the Smol-V stages into SPIR-V. Validate stage counts and decoded magic across the full cache, including custom `.gdshader` variants.
3. Feed the decoded shaders to `vk_shaders.py` if the runtime uses Vulkan, then survey any shaders generated after launch. If it uses NVN, identify the actual NVN program data instead.
4. Refresh nxkit's nxnative pin and patches, generate a provisional profile for this exact build, and run the PC preparation and cloud build.
5. Test the IPA on a device; use `Documents/log.txt` to debug boot, rendering, audio and memory before marking the game playable.
