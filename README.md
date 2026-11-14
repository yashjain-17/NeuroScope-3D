# NeuroScope 3D

**Research and teaching prototype for 3D brain MRI segmentation exploration.**

NeuroScope 3D contains a FastAPI backend for validating four-modality NIfTI study sets, running a MONAI-based segmentation pipeline, calculating region volumes, and generating reports. It is not a diagnostic product or a medical device.

> **Important:** For research and teaching only. Never use the output for diagnosis, treatment, triage, or patient-care decisions.

## Repository layout

- `backend/main.py` — FastAPI application and API routes
- `backend/app/` — configuration, validation, inference, volumetrics, database, and PDF generation
- `backend/requirements.txt` — Python dependencies
- `docs/` — product, architecture, rules, and task documentation
- `MODEL_CARD.md` — model documentation

## Requirements

- Python 3.10 or newer (use a version supported by the installed PyTorch/MONAI wheels)
- pip and a virtual environment
- Sufficient RAM and disk space for 3D MRI volumes
- A compatible CUDA setup is optional; the code falls back to CPU

## Backend setup

Run these commands from the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API documentation is available at `http://127.0.0.1:8000/docs` while the server is running.

## Input data

The validation route expects four NIfTI volumes:

- T1
- T1Gd (post-contrast T1)
- T2
- FLAIR

An expert mask may optionally be supplied for evaluation workflows. Use only authorized, de-identified research data. Confirm image orientation, alignment, dimensions, affine transforms, and voxel spacing before interpreting any result.

## Region terminology

- **WT (whole tumour):** NCR + ED + ET
- **TC (tumour core):** NCR + ET
- **ET (enhancing tumour):** enhancing tumour label

Volume calculations are meaningful only when the image geometry and voxel spacing are valid.

## Known limitations — read before use

- The current inference module constructs a SegResNet architecture but does not load a documented pretrained checkpoint. Until a validated checkpoint and reproducible preprocessing pipeline are integrated, predictions must be treated as experimental/unvalidated.
- The repository tree currently contains a backend but no checked-in frontend application.
- A successful API response or 3D rendering is not evidence of clinical accuracy.
- Security, access control, retention, deployment hardening, and independent model validation must be completed before any wider deployment.

## Research validation checklist

Record dataset provenance and permissions, model/checkpoint hash, preprocessing settings, modality registration, voxel spacing, expert-label protocol, evaluation metrics, failure cases, and software versions for every experiment.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep model claims evidence-based and never remove the research-only disclaimer.

## License

See the repository license file, if present. Check the terms of each dataset, model checkpoint, and dependency separately.
