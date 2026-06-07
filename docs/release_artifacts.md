# Release Artifact Verification

Release artifacts are verified locally before publishing. The verification step checks the built wheel, source distribution, and wheel metadata so packaging issues are caught before a tag or GitHub release is created.

## Build artifacts

```bash
rm -rf dist build *.egg-info
python -m build
```

Expected files for `1.0.0rc1` are:

- `dist/hallucination_replay_system-1.0.0rc1-py3-none-any.whl`
- `dist/hallucination_replay_system-1.0.0rc1.tar.gz`

For the final `1.0.0` release, replace `1.0.0rc1` with `1.0.0`.

## Verify artifacts

```bash
python scripts/verify_release_artifacts.py --version 1.0.0rc1
```

The verification script checks:

- the wheel exists for the expected version;
- the source distribution exists for the expected version;
- wheel metadata contains the package name, version, and summary;
- public package import roots are included in the wheel;
- README, project metadata, source package, and smoke tests are included in the source distribution.

This does not publish anything. Publishing remains a separate explicit release step.
