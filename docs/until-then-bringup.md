# Until Then (010019C023004000) bring-up

Status: IPA built and ZIP integrity checked for update v1.0.9. Gameplay has not been tested on an iPhone.

## Package and build

- Base v0 and update v589824; update `main` build ID `53e2366a73ef1a06f185c5d80c13d642`.
- SDK 19. Both NSZ files were decompressed to NSP with NCA hash verification.
- The merged RomFS image is 4,069,673,746 bytes and contains the base game plus update.
- nxnative is pinned to `e5620b1a05a5b7374e0135d6312d3e90994eab81`.
- GitHub Actions run [42039714477](https://github.com/Flamelovers/nxkit/actions/runs/42039714477) successfully built the slim IPA. The local merge produced `UntilThen-v1.0.9.ipa` (4,187,750,997 bytes); `zipfile.testzip()` returned no errors.

## Graphics work

- This is a Godot game with Vulkan shader caches. `tools/godot_cache_extract.py` reads the `GDSC`/`GSBD` cache records and the Godot Smol-V decoder expands them into SPIR-V during the cloud build.
- The build decoded 3,364 unique SPIR-V shaders. The Metal output is split into 26 libraries of at most 128 functions; `hle_vk.m` loads each library by the index recorded in `vk_shaders.tsv`.
- Godot's second color output is a second render target, so this game disables nxnative's dual-source blend shader variant.
- The current Vulkan translator skips 72 compute shader stages. Rendering and gameplay may therefore fail or be incomplete. The selected renderer and runtime shader usage need testing on a device.

## Next validation

Install the IPA on a compatible iPhone and inspect `Documents/log.txt` after launch. Verify boot, graphics, input, audio and memory. Capture missing shader modules or unsupported Vulkan calls and extend the bridge before describing the game as playable.
