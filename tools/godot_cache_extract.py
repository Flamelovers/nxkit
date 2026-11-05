#!/usr/bin/env python3
"""Extract Smol-V stages from Godot 4.3 GDSC/GSBD Vulkan shader caches.

The companion .NET tool decodes the Smol-V files into SPIR-V. Game data stays
outside the repository. This parser follows Godot 4.3 shader_rd.cpp and
rendering_device_driver_vulkan.cpp; unexpected versions/layouts fail closed.
"""
import argparse
import hashlib
import struct
import sys
from pathlib import Path

DATA_SIZE = 56
BINDING_SIZE = 20
SPEC_SIZE = 16


def u32(data, offset):
    if offset + 4 > len(data):
        raise ValueError('truncated cache')
    return struct.unpack_from('<I', data, offset)[0]


def padded(size):
    return (size + 3) & ~3


def stages(data):
    if len(data) < 12 or data[:4] != b'GDSC' or u32(data, 4) != 3:
        raise ValueError('not a Godot 4.3 shader cache')
    offset = 12
    variants = u32(data, 8)
    if variants > 4096:
        raise ValueError('implausible variant count')
    for variant in range(variants):
        size = u32(data, offset)
        offset += 4
        end = offset + size
        if end > len(data):
            raise ValueError('truncated variant')
        if not size:
            continue
        blob = data[offset:end]
        offset = end
        if len(blob) < 12 + DATA_SIZE or blob[:4] != b'GSBD' or u32(blob, 4) != 4 or u32(blob, 8) != DATA_SIZE:
            raise ValueError(f'variant {variant}: unknown GSBD version or layout')
        fields = struct.unpack_from('<Q11I', blob, 12)
        spec_count, set_count, stage_count, name_len = fields[2], fields[7], fields[10], fields[11]
        if spec_count > 4096 or set_count > 32 or stage_count > 8 or name_len > 4096:
            raise ValueError(f'variant {variant}: implausible counts')
        pos = 12 + DATA_SIZE + padded(name_len)
        for _ in range(set_count):
            n = u32(blob, pos)
            pos += 4 + n * BINDING_SIZE
            if n > 4096 or pos > len(blob):
                raise ValueError('invalid binding table')
        pos += spec_count * SPEC_SIZE
        if pos > len(blob):
            raise ValueError('invalid specialization table')
        for _ in range(stage_count):
            stage, smolv_size, zstd_size = struct.unpack_from('<III', blob, pos)
            pos += 12
            if stage > 7 or smolv_size > 1 << 26 or zstd_size > 1 << 26:
                raise ValueError('invalid stage header')
            length = zstd_size or smolv_size
            content = blob[pos:pos + length]
            if len(content) != length:
                raise ValueError('truncated stage')
            pos += padded(length)
            if zstd_size:
                from compression import zstd
                content = zstd.decompress(content)
                if len(content) != smolv_size:
                    raise ValueError('wrong decompressed Smol-V size')
            yield variant, stage, content
        if pos != len(blob):
            raise ValueError(f'variant {variant}: {len(blob) - pos} trailing bytes')
    if offset != len(data):
        raise ValueError(f'{len(data) - offset} trailing cache bytes')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('romfs')
    ap.add_argument('output')
    ap.add_argument('--nxnative', help='nxnative checkout, needed for RomFS.img input')
    a = ap.parse_args()
    root, out = Path(a.romfs), Path(a.output)
    if root.is_file():
        if not a.nxnative:
            raise SystemExit('--nxnative is required for a RomFS.img input')
        sys.path.insert(0, str(Path(a.nxnative) / 'dm/tools'))
        from romfs import Path as RomPath
        root = RomPath(root)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted((root / 'shader_cache').rglob('*.vulkan.cache'))
    if not files:
        raise SystemExit('no Godot Vulkan shader caches')
    total = 0
    unique = set()
    for path in files:
        for variant, stage, content in stages(path.read_bytes()):
            total += 1
            digest = hashlib.sha256(content).hexdigest()
            if digest not in unique:
                (out / (digest + '.smolv')).write_bytes(content)
                unique.add(digest)
    print(f'{len(files)} caches, {total} stages, {len(unique)} unique Smol-V shaders')


if __name__ == '__main__':
    main()
