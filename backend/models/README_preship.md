Preship model instructions

This file documents how to add a preshipped model binary to the repository and the legal checks required.

Steps to add the model weights locally:
1. Download the model files and place them under the path listed in backend/models/manifest.json (the "local_path" field). Example: models/davidau-llama-3.2-8x3b-moe/
2. Ensure the model format (GGUF, GGML, ONNX, Torch) is supported by your local runtime and that any required adapter or tokenizer files are present.
3. Update the manifest entry if the model is image-capable (set "modalities" to include "image") only if you have verified that the model supports image inputs (e.g., it includes vision encoder or multimodal adapters).
4. Confirm licensing: before committing or distributing the model weights with this repository, you MUST ensure you have explicit permission to redistribute them and that doing so does not violate the model's license, terms of service, or export controls.

Operational safeguards (recommended):
- Enforce forensic prompt config by default for this model (backend/config/forensic_prompt.json).
- Add an admin-only switch to enable/disable preshipped models and to control visibility of GPS or sensitive metadata.
- Keep an audit log of any use of preshipped models, including operator identity, timestamp, model hash, and inputs/outputs.

By proceeding with preshipping, you confirm you have the legal right to distribute the specified model and understand the compliance responsibilities.
