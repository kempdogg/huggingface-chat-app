Kali AI Assistant — v1.1.0

Summary
- Renamed app to "Kali AI assistant".
- Major fixes and improvements to image handling and forensic analysis features.
- Improved pre-downloaded model support for image processing.
- Reduced imaginative/storytelling responses for forensic workflows.

Included preshipped model
- This release includes a preship manifest entry for the requested model:
  hf.co/DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF:Q4_K_M

Changes
- Rename:
  - UI and package metadata updated to "Kali AI assistant".

- Photo & image processing:
  - Fixed image aspect/preview handling on the frontend (ensures proper aspect ratio and orientation).
  - Add automatic EXIF/IPTC metadata extraction (device make/model, capture datetime, GPS location if present).
  - Use pre-downloaded image-capable models (when present) to extract visual attributes (scene tags, objects, non-identifying face attributes like age-range/approximate gender/face bounding boxes).
  - If GPS or other sensitive metadata is found, it is presented as raw evidence only; do not attempt to infer or assert identity.

- Model behavior & configuration:
  - Default system prompt now forces forensic/factual mode (low creativity).
  - Model generation settings (temperature, top_p) configured to minimize hallucination.
  - Prevent generative storytelling in response to factual queries by using a dedicated analysis model or constrained prompt.

- Security & compliance:
  - Added explicit reminders to verify legal authority before using the app for investigative tasks.
  - Audit logging added for image analysis operations.

Notes
- The app will extract "all available information that is embedded in the image" (EXIF/IPTC) and use local image models for object/scene analysis where available. The app will not attempt to deanonymize or identify specific private individuals or provide assistance to perform exploitation.

Caveat about preshipping third-party models
- You asked to preship the model hosted at hf.co/DavidAU/...: please confirm you have the legal right and licence permission to redistribute that model within this repository and that you accept responsibility for complying with the model's license and any export controls or usage restrictions.
