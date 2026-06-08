# Release Artifact Verification

Release artifacts are verified locally before publishing. The verification step checks the built wheel, source distribution, and wheel metadata so packaging issues are caught before a tag or GitHub release is created.

## Build artifacts

```bash
rm -rf dist build *.egg-info
python -m build
```

Expected files for the final `1.0.0` release are:

- `dist/hallucination_replay_system-1.0.0-py3-none-any.whl`
- `dist/hallucination_replay_system-1.0.0.tar.gz`

Release candidates use the same file pattern with the candidate suffix, for example `1.0.0rc1`.

## Verify artifacts

For the final release:

```bash
python scripts/verify_release_artifacts.py --version 1.0.0
```

For the previous release candidate:

```bash
python scripts/verify_release_artifacts.py --version 1.0.0rc1
```

The verification script checks:

- the wheel exists for the expected version;
- the source distribution exists for the expected version;
- wheel metadata contains the package name, version, and summary;
- public package import roots are included in the wheel;
- README, project metadata, source package, and smoke tests are included in the source distribution.

This does not publish anything. Publishing remains a separate explicit release step after tests, coverage, linting, type checks, build, artifact verification, and repository validation all pass.

## Final gate

Before tagging `v1.0.0`, run:

```bash
pytest
pytest --cov
ruff check .
mypy .
python -m build
python scripts/verify_release_artifacts.py --version 1.0.0
python scripts/validate_repo.py
```

The package version in `pyproject.toml` and `src/hallucination_replay/_version.py` must both be `1.0.0` before artifact verification is run for the final release.
