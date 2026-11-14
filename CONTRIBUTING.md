# Contributing to NeuroScope 3D

Thank you for helping improve this research and teaching prototype.

## Scope and safety

- Keep the project explicitly research/education-only; do not describe it as a diagnostic tool.
- Do not add identifiable patient data, private scans, credentials, or licensed datasets without permission.
- Do not claim model accuracy without a documented evaluation protocol and evidence.
- Preserve provenance for datasets, model weights, preprocessing, and evaluation outputs.

## Development workflow

1. Create a focused branch from the default branch.
2. Explain the research or engineering problem before changing code.
3. Keep changes small and reviewable.
4. Add or update tests for validation, geometry, volume calculations, and failure handling.
5. Run relevant checks locally and record the environment and command used.
6. Update README/docs when API behavior, dependencies, model configuration, or data requirements change.

## Model changes

Document checkpoint source and license, cryptographic hash, architecture, preprocessing, input modalities, label mapping, inference settings, and independent evaluation results. Never silently substitute random/untrained weights for a validated checkpoint.

## Pull requests

Include purpose, scope, files changed, tests performed, known limitations, and screenshots or sample outputs when relevant. Use only synthetic or authorized de-identified data in examples.

## Review checklist

- [ ] No patient-identifying data or secrets included
- [ ] Research-only disclaimer retained
- [ ] Tests and validation evidence included
- [ ] Model/data provenance documented
- [ ] Documentation updated
