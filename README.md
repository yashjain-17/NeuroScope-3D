# NeuroScope 3D

**See a brain tumour in 3D, measure it, and understand the limits of the model.**

NeuroScope 3D is a research and teaching prototype for exploring brain MRI segmentation results in 3D. It is intended to support learning, visualization, and reproducible experimentation—not diagnosis or clinical decision-making.

> **Medical disclaimer:** This project is not a medical device. Model outputs may be incorrect and must not be used to make patient-care decisions.

## Project goals

- Visualize suspected tumour regions from multi-modal brain MRI.
- Explore whole-tumour (WT), tumour-core (TC), and enhancing-tumour (ET) regions.
- Calculate region volumes in millilitres when valid voxel-spacing metadata is available.
- Communicate uncertainty and limitations rather than presenting predictions as ground truth.
- Support research-lab and radiology-teaching workflows using authorized, de-identified data.

## MRI modalities

The intended four-modality input set is:

- **T1** — native T1-weighted MRI
- **T1Gd** — post-contrast T1-weighted MRI
- **T2** — T2-weighted MRI
- **FLAIR** — fluid-attenuated inversion recovery

Region definitions:

- **WT:** NCR + ED + ET
- **TC:** NCR + ET
- **ET:** enhancing tumour

## Data safety

- Use only data you are authorized to process.
- Use de-identified research data; do not upload identifiable patient information.
- Treat segmentations, measurements, and generated reports as experimental outputs.
- Have qualified experts review research interpretations.
- Do not claim clinical accuracy without independent validation on an appropriate dataset.

## Validation checklist

Before relying on results for research conclusions, verify the model checkpoint and provenance, preprocessing, modality alignment, voxel spacing, evaluation protocol, and reproducibility of the complete pipeline. A 3D visualization alone does not establish segmentation accuracy.

## Future work

- Documented model checkpoints and reproducible inference.
- Independent evaluation against expert-labelled datasets.
- Better uncertainty calibration and failure-case visualization.
- Secure study management, audit trails, and controlled data retention.
- Accessible 3D review tools for research and teaching.

## Disclaimer

NeuroScope 3D is provided for educational and research use only. It does not provide a diagnosis or treatment recommendation and is not a substitute for professional medical judgment.
