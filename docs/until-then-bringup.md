# Until Then (010019C023004000) bring-up

Status: IPA built and ZIP integrity checked for update v1.0.9. Gameplay has not been tested on an iPhone.

An iPhone launch log subsequently showed that the bundled RomFS mounted successfully, but Godot failed to create its Vulkan context (`_initialize_devices`, `ERR_CANT_CREATE`) and the display server. The black screen is therefore a graphics bridge issue, not a missing-resource symptom.

The subsequent separate-resource log confirmed that `Documents/romfs.img` mounted, and `DM_VK_LOG=1` produced no bridge calls. `ro::LookupSymbol` resolved `vkGetInstanceProcAddr` and `vkGetDeviceProcAddr` to the loaded Nintendo Vulkan `subsdk1` module. Game patch `0003-ro-vulkan-bridge.patch` routes those two lookups to nxnative's host Vulkan bridge. [Cloud run 42051226101](https://github.com/Flamelovers/nxkit/actions/runs/42051226101) built a replacement shell; device testing is still required to learn whether later Vulkan calls also need work.

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

## Separate app and resources

`python nxkit.py shell <slim-or-full.ipa> <build/nxkit.json> -o <shell.ipa>` removes bundled `romfs/`, `romfs.img`, and `aoc/` entries and adds a `romfs.id` that matches the extracted image. Transfer that image to the app's `Documents/romfs.img` once. Later app changes can use the same image as long as the game version is unchanged; generate only a new shell IPA. The app's bundle ID is `org.nxnative.010019c023004000`, and file sharing is enabled.
