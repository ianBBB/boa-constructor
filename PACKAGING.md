# Packaging and PyPI Release Guide

This project uses setuptools with `pyproject.toml` + `setup.py`.

## One-command Helper

Use the bundled PowerShell helper to run clean + build + check in one step:

```powershell
.\release.ps1
```

Optional flags:

- `-NoClean` skip deletion of previous artifacts
- `-NoCheck` skip `twine check`
- `-PythonExe <path>` use a different Python interpreter

Use the upload helper to push artifacts to TestPyPI:

```powershell
.\upload-testpypi.ps1
```

Optional flags:

- `-SkipCheck` skip `twine check` before upload
- `-PythonExe <path>` use a different Python interpreter

## Prerequisites

- Python 3.9+
- `build` and `twine` installed

```powershell
python -m pip install -U build twine
```

If needed, use `py -m ...` on Windows or pass `-PythonExe` to the helper scripts.

## 1. Bump Version

Update `__version__.py`:

- `version = 'X.Y.Z'`

Keep the version in `__version__.py` as the single source of truth.

## 2. Clean Previous Artifacts

```powershell
Remove-Item -Recurse -Force dist, build, *.egg-info
```

## 3. Build Distributions

```powershell
python -m build --no-isolation
python -m build --wheel --no-isolation
```

Expected output in `dist/`:

- `boa_constructor-<version>.tar.gz`
- `boa_constructor-<version>-py3-none-any.whl`

## 4. Validate Metadata and README Rendering

```powershell
python -m twine check dist/*
```

Both files should report `PASSED`.

## 5. Upload to TestPyPI (Recommended)

```powershell
python -m twine upload --repository testpypi dist/*
```

Verify install from TestPyPI in a clean virtual environment.

## 6. Upload to PyPI

```powershell
python -m twine upload dist/*
```

Optional token file location (user home):

- `$HOME/.pypirc` (PowerShell also supports `~/.pypirc`)

## 7. Tag Release in Git

```powershell
git tag v<version>
git push origin v<version>
```

## Notes

- Package name: `boa-constructor`
- Console entry point: `boa`
- GUI entry point: `boa-gui`
- Build backend config is in `pyproject.toml`.
- Distribution metadata and package inclusion rules are in `setup.py` and `MANIFEST.in`.
