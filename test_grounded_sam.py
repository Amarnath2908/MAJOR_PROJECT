"""
test_grounded_sam.py — Standalone GroundingDINO + SAM Integration Test
=======================================================================
Tests the full DINO → SAM pipeline without FastAPI.

Run from the project root using the DesignVerse venv:
    venv\Scripts\python test_grounded_sam.py

Expected outputs:
    grounded_sam_output.jpg      -- annotated image with bounding boxes
    grounded_sam_mask_001.png    -- binary mask for detection #1
    grounded_sam_mask_002.png    -- binary mask for detection #2
    etc.
"""

import sys
import os
import time
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
GROUNDING_DINO_ROOT = Path("D:/AI/GroundingDINO")
DINO_CONFIG = GROUNDING_DINO_ROOT / "groundingdino/config/GroundingDINO_SwinT_OGC.py"
DINO_CHECKPOINT = GROUNDING_DINO_ROOT / "weights/groundingdino_swint_ogc.pth"
SAM_CHECKPOINT = GROUNDING_DINO_ROOT / "weights/sam/sam_vit_b_01ec64.pth"
TEST_IMAGE = GROUNDING_DINO_ROOT / "test_image.webp"

TEXT_PROMPT = "sofa"
BOX_THRESHOLD = 0.30
TEXT_THRESHOLD = 0.25
DEVICE = "cpu"

OUTPUT_DIR = Path(".")


def verify_paths():
    """Verify all required files exist before loading models."""
    errors = []
    for p, name in [
        (DINO_CONFIG, "DINO config"),
        (DINO_CHECKPOINT, "DINO checkpoint"),
        (SAM_CHECKPOINT, "SAM checkpoint"),
        (TEST_IMAGE, "test image"),
    ]:
        if not p.exists():
            errors.append(f"MISSING {name}: {p}")
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    print("[OK] All paths verified.")


def load_groundingdino():
    """Load GroundingDINO model once."""
    print(f"\n[PHASE 4] Loading GroundingDINO from {DINO_CONFIG}")
    from groundingdino.util.inference import load_model
    model = load_model(str(DINO_CONFIG), str(DINO_CHECKPOINT), device=DEVICE)
    model.eval()
    print("[OK] GroundingDINO loaded.")
    return model


def load_sam():
    """Load SAM ViT-B model once."""
    print(f"\n[PHASE 4] Loading SAM ViT-B from {SAM_CHECKPOINT}")
    from segment_anything import SamPredictor, sam_model_registry
    sam = sam_model_registry["vit_b"](checkpoint=str(SAM_CHECKPOINT))
    sam.to(DEVICE)
    sam.eval()
    predictor = SamPredictor(sam)
    print("[OK] SAM loaded.")
    return predictor


def run_groundingdino(dino_model, image_path: Path, prompt: str):
    """
    Run GroundingDINO detection on a single image.
    Returns list of dicts with label, confidence, normalized box.
    """
    import torch
    from groundingdino.util.inference import load_image, predict

    print(f"\n[PHASE 5] Running GroundingDINO: prompt='{prompt}'")
    t0 = time.time()

    image_source, image_tensor = load_image(str(image_path))
    # image_source is a numpy HWC RGB array

    with torch.no_grad():
        boxes, logits, phrases = predict(
            model=dino_model,
            image=image_tensor,
            caption=prompt,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD,
            device=DEVICE,
        )

    elapsed = time.time() - t0
    print(f"[OK] DINO inference: {len(boxes)} detections in {elapsed:.2f}s")

    # boxes are normalized [cx, cy, w, h] in [0,1]
    detections = []
    for i, (box, logit, phrase) in enumerate(zip(boxes.tolist(), logits.tolist(), phrases)):
        detections.append({
            "idx": i,
            "label": phrase,
            "confidence": round(logit, 4),
            "norm_box": box,  # [cx, cy, w, h]
        })
        print(f"  Detection {i+1}: label='{phrase}' conf={logit:.4f} box={[round(v,4) for v in box]}")

    return image_source, detections


def convert_boxes_to_pixels(norm_boxes, image_width: int, image_height: int):
    """
    Convert normalized [cx, cy, w, h] boxes → pixel [x1, y1, x2, y2].
    Clamps to image boundaries.
    """
    pixel_boxes = []
    for box in norm_boxes:
        cx, cy, w, h = box
        x1 = max(0, int((cx - w / 2) * image_width))
        y1 = max(0, int((cy - h / 2) * image_height))
        x2 = min(image_width, int((cx + w / 2) * image_width))
        y2 = min(image_height, int((cy + h / 2) * image_height))
        pixel_boxes.append([x1, y1, x2, y2])
    return pixel_boxes


def run_sam(predictor, image_rgb, pixel_boxes):
    """
    Run SAM on the image using pixel bounding boxes from DINO.
    Returns list of (mask_array, score) tuples.
    """
    import numpy as np
    import torch

    print(f"\n[PHASE 6] Running SAM on {len(pixel_boxes)} bounding boxes")
    predictor.set_image(image_rgb)

    all_masks = []
    for i, box in enumerate(pixel_boxes):
        x1, y1, x2, y2 = box
        input_box = np.array([x1, y1, x2, y2])

        with torch.no_grad():
            masks, scores, _ = predictor.predict(
                box=input_box,
                multimask_output=True,
            )

        # Pick the mask with highest score
        best_idx = scores.argmax()
        best_mask = masks[best_idx]
        best_score = float(scores[best_idx])

        all_masks.append((best_mask, best_score))
        print(f"  SAM mask {i+1}: shape={best_mask.shape} score={best_score:.4f} box={box}")

    return all_masks


def save_annotated_image(image_rgb, detections, pixel_boxes, output_path: Path):
    """Save an annotated JPEG showing bounding boxes + labels."""
    import cv2
    import numpy as np

    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    for det, box in zip(detections, pixel_boxes):
        x1, y1, x2, y2 = box
        cv2.rectangle(image_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label_text = f"{det['label']} {det['confidence']:.2f}"
        cv2.putText(
            image_bgr, label_text, (x1, max(0, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2,
        )
    cv2.imwrite(str(output_path), image_bgr)
    print(f"[SAVED] Annotated image: {output_path}")


def save_masks(masks_and_scores, detections, output_dir: Path):
    """Save each binary mask as a PNG (0=background, 255=object)."""
    import cv2
    import numpy as np

    mask_paths = []
    for i, ((mask, score), det) in enumerate(zip(masks_and_scores, detections)):
        binary_mask = (mask * 255).astype(np.uint8)
        mask_path = output_dir / f"grounded_sam_mask_{i+1:03d}.png"
        cv2.imwrite(str(mask_path), binary_mask)
        mask_paths.append(mask_path)
        print(f"[SAVED] Mask {i+1}: {mask_path}  shape={binary_mask.shape}")
    return mask_paths


def main():
    print("=" * 60)
    print("GroundingDINO + SAM Integration Test")
    print("=" * 60)
    print(f"Python:      {sys.executable}")
    print(f"Test image:  {TEST_IMAGE}")
    print(f"Prompt:      '{TEXT_PROMPT}'")
    print(f"Device:      {DEVICE}")
    print(f"DINO config: {DINO_CONFIG}")
    print(f"DINO ckpt:   {DINO_CHECKPOINT}")
    print(f"SAM ckpt:    {SAM_CHECKPOINT}")

    # Step 1: Verify paths
    verify_paths()

    # Step 2: Load models
    dino_model = load_groundingdino()
    sam_predictor = load_sam()

    # Step 3: Load test image
    from PIL import Image
    import numpy as np
    pil_img = Image.open(TEST_IMAGE).convert("RGB")
    image_width, image_height = pil_img.size
    print(f"\n[INFO] Image size: {image_width}x{image_height}")

    # Step 4: Run GroundingDINO
    image_rgb, detections = run_groundingdino(dino_model, TEST_IMAGE, TEXT_PROMPT)

    if not detections:
        print("\n[WARN] No detections found. Try lowering BOX_THRESHOLD.")
        return

    # Step 5: Convert normalized DINO boxes to pixel coordinates
    norm_boxes = [d["norm_box"] for d in detections]
    pixel_boxes = convert_boxes_to_pixels(norm_boxes, image_width, image_height)
    print(f"\n[INFO] Pixel bounding boxes:")
    for i, (det, box) in enumerate(zip(detections, pixel_boxes)):
        print(f"  [{i+1}] {det['label']}  conf={det['confidence']:.4f}  px_box={box}")

    # Step 6: Run SAM
    masks_and_scores = run_sam(sam_predictor, image_rgb, pixel_boxes)

    # Step 7: Save outputs
    print("\n[SAVING] Outputs...")
    annotated_path = OUTPUT_DIR / "grounded_sam_output.jpg"
    save_annotated_image(image_rgb, detections, pixel_boxes, annotated_path)
    mask_paths = save_masks(masks_and_scores, detections, OUTPUT_DIR)

    # Step 8: Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Image:        {TEST_IMAGE.name}  ({image_width}x{image_height})")
    print(f"Prompt:       '{TEXT_PROMPT}'")
    print(f"Detections:   {len(detections)}")
    for i, (det, box, (mask, score)) in enumerate(zip(detections, pixel_boxes, masks_and_scores)):
        print(f"\n  Object {i+1}:")
        print(f"    label:      {det['label']}")
        print(f"    confidence: {det['confidence']:.4f}")
        print(f"    pixel bbox: x1={box[0]} y1={box[1]} x2={box[2]} y2={box[3]}")
        print(f"    mask shape: {mask.shape}")
        print(f"    mask score: {score:.4f}")
        print(f"    mask file:  {mask_paths[i].name}")
    print(f"\n  Annotated:  {annotated_path.name}")
    print("=" * 60)
    print("[SUCCESS] Standalone test complete.")


if __name__ == "__main__":
    main()
