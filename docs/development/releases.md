# Release Process

## Release Workflow

1. **Version Update**: Update version in `setup.py` and `__init__.py`
2. **Changelog**: Update CHANGELOG.md with new features and fixes
3. **Documentation**: Ensure documentation is up to date
4. **Testing**: Run comprehensive vibe tests
5. **Tag Release**: Create git tag and GitHub release
6. **Deploy**: Automated deployment to PyPI and GitHub Pages

## Version Scheme

OllamaPy follows semantic versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)  
- Patch: Bug fixes

## Release Types

- **Alpha**: Early development releases
- **Beta**: Feature-complete pre-releases
- **Release Candidate**: Final testing before release
- **Stable**: Production-ready releases