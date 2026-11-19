# Stream-1 test branch

This branch is isolated from `main` and the pre-existing `builds` branch.

## Test URLs

- Test repository: `https://raw.githubusercontent.com/Abhishekred/Stream-1/test/repo.json`
- Test plugin manifest: `https://raw.githubusercontent.com/Abhishekred/Stream-1/test/plugins.json`
- Mirrored repository (after successful workflow run): `https://raw.githubusercontent.com/Abhishekred/Stream-1/test-builds/repo.json`
- Mirrored plugin manifest (after successful workflow run): `https://raw.githubusercontent.com/Abhishekred/Stream-1/test-builds/plugins.json`

The `test` branch's `plugins.json` links directly to Phisher98's published builds. The `test-builds` branch, when published by GitHub Actions, stores separate copies of the existing `.cs3` extension binaries and its own matching manifest.

## Publishing test builds

The `Publish test CloudStream builds` workflow executes on changes to the test branch's manifest, sync script, or workflow, provided GitHub Actions is enabled and the workflow token can write repository contents. It:

1. Downloads each extension from its upstream source URL.
2. Checks each binary against its SHA-256 checksum and declared size.
3. Publishes the verified assets, `plugins.json`, and `repo.json` into the separate `test-builds` branch.
4. Leaves `main` and `builds` untouched.

**Important:** This is a verified binary mirror, **not** a Kotlin/Gradle source build. This repository currently does not contain the plugin sources. The original plugin authors and source repository references remain in the plugin metadata.

Do not use `test-builds` in production until the workflow succeeds and the raw URLs return valid content. Ensure you have permission to redistribute upstream binaries before public use.
