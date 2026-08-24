# Model Research Log: Ghost Mannequin MVP

This document tracks all AI models evaluated for the Ghost Mannequin pipeline, with strict adherence to commercial viability, cost, and garment fidelity.

## 1. Background Removal / Segmentation

### rembg (U2-Net / IS-Net)
- **License:** MIT (Commercial use allowed)
- **Feasibility:** High. Runs fast on CPU via ONNX Runtime.
- **Quality:** Excellent for general foreground extraction.
- **Decision:** **ACCEPTED (Phase 1 Baseline)**

### BRIA RMBG 1.4 / 2.0
- **License:** CC BY-NC 4.0 (Non-commercial only)
- **Feasibility:** Rejected purely on license.
- **Decision:** **REJECTED**

### Segment Anything Model (SAM / SAM 2)
- **License:** Apache 2.0
- **Feasibility:** Too slow for CPU-only inference (30-60x slower than GPU).
- **Decision:** **DEFERRED (Monitor for GPU Phase)**

---

## 2. Structural & Image Generation

### Stable Diffusion 1.5 (Inpainting)
- **License:** CreativeML Open RAIL-M (Commercial use allowed)
- **Feasibility:** Requires GPU (4-8GB VRAM). Too slow for CPU.
- **Quality:** Good for filling the neck gap, but risks hallucinating if not tightly constrained via masks.
- **Decision:** **ACCEPTED FOR PHASE 2 (GPU required)**

### SDXL
- **License:** CreativeML Open RAIL++-M
- **Feasibility:** High VRAM requirements (8-16GB+).
- **Decision:** **DEFERRED (Too heavy for MVP)**

### ControlNet (Depth / Canny)
- **License:** Open RAIL-M
- **Feasibility:** Same as SD 1.5. Excellent for maintaining structural consistency during the inpainting phase.
- **Decision:** **ACCEPTED FOR PHASE 2**

### IP-Adapter
- **License:** Apache 2.0
- **Feasibility:** Helps condition the diffusion model on garment textures.
- **Decision:** **DEFERRED (Will investigate if Phase 2 fidelity is low)**

---

## 3. Virtual Try-On (VTON) Architectures

The following models were investigated for their architecture, but their weights are strictly non-commercial. We cannot use them in ClothMatics.

- **CatVTON:** CC BY-NC-SA 4.0 -> **REJECTED**
- **IDM-VTON:** CC BY-NC-SA 4.0 -> **REJECTED**
- **OOTDiffusion:** CC BY-NC-SA 4.0 -> **REJECTED**
- **HR-VITON:** CC BY-NC 4.0 -> **REJECTED**

---

## Conclusion
The winning strategy for the **Zero-Cost MVP** is a purely deterministic **Phase 1** using `rembg` (MIT license, CPU-friendly) for segmentation + geometrical centering/shadowing. 

**Phase 2** will introduce SD 1.5 Inpainting + ControlNet (Open RAIL-M) specifically targeting only the mannequin's internal collar gap, while preserving 100% of the original exterior garment pixels using Mask-Aware Blending.
