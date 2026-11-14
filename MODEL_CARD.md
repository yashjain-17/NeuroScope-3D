# NeuroScope 3D — Model Card

## Intended use

NeuroScope 3D is a research and teaching prototype for exploring multimodal brain MRI segmentation workflows, volumetric measurements, and model-evaluation concepts. It is not a medical device and must not be used for diagnosis, treatment selection, triage, or other clinical decisions.

## Model availability and current status

The repository defines a MONAI SegResNet architecture with four MRI input channels and three nested tumour-region output channels. **A trained model checkpoint is not included in this repository.** The architecture definition alone is not a trained model.

To prevent random initial weights from being mistaken for a meaningful segmentation, inference now fails closed unless a compatible trained checkpoint is explicitly configured through `NEUROSCOPE_MODEL_CHECKPOINT`. The checkpoint must match the architecture and output-channel semantics described by the training pipeline. Loading is strict; incompatible checkpoints are rejected.

## Inputs and outputs

- Inputs: co-registered 3D T1, T1Gd, T2, and FLAIR NIfTI volumes.
- Outputs: a NIfTI label map using BraTS-style labels (NCR=1, ED=2, ET=4), plus derived volumetric measurements.
- Expected modality alignment: matching spatial dimensions and affine transforms.

## Training and validation

No training dataset, training script, checkpoint provenance, independent test results, calibration study, or clinical validation evidence is currently supplied by this repository. Do not infer model accuracy, sensitivity, specificity, Dice score, or clinical readiness from the presence of the architecture code.

Before research use, document the checkpoint's source, exact architecture/configuration, training data provenance and licensing, preprocessing, training procedure, independent validation cohort, region-wise metrics, failure analysis, and limitations.

## Known limitations

- A checkpoint is not bundled; segmentation remains unavailable until one is supplied.
- The current preprocessing and thresholding pipeline requires validation against the exact checkpoint's training configuration.
- Segmentation uncertainty is not calibrated or clinically validated.
- Volumetric values depend on input geometry and segmentation quality.
- The skull-stripping indicator is a heuristic, not a definitive quality-control test.

## Safety statement

**Research and teaching only. Not for diagnosis or clinical decision-making.** A qualified researcher must review all inputs, outputs, and measurements. Never use an unvalidated model output to guide patient care.
