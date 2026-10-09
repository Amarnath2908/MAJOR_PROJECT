"""
ai/image_editor.py — AI Image Editor Interface
===============================================
Placeholder class for the inpainting/editing AI model (Stable Diffusion / FLUX).

When to replace this file
--------------------------
When integrating Stable Diffusion or FLUX:
  1. pip install diffusers transformers accelerate
  2. Authenticate with HuggingFace hub.
  3. Replace edit() with real inpainting inference.

DO NOT import diffusers or transformers here yet.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class ImageEditor:
    """
    Interface class for the AI image editing / inpainting model.

    In the final integration, this class will:
    1. Accept a source image and a text prompt.
    2. Use SAM to generate a segmentation mask for the relevant region.
    3. Feed the image, mask, and prompt to Stable Diffusion's inpainting pipeline.
    4. Return the path to the newly generated edited image.

    At this stage, edit() returns a mock path.

    Usage
    -----
        editor = ImageEditor()
        result = editor.edit("storage/uploads/room.jpg", "Paint the walls grey")
        # → "storage/edited/sample.png"
    """

    def __init__(self) -> None:
        """
        Initialise the ImageEditor interface.

        Real implementation will:
        - Load the Stable Diffusion inpainting pipeline.
        - Optionally load a LoRA adapter for style fine-tuning.
        - Move pipeline to CUDA if available.
        """
        logger.info(
            "ImageEditor placeholder initialised. "
            "Real model will be loaded here during integration."
        )

    def edit(self, image_path: str, prompt: str) -> str:
        """
        Edit an image using a natural language prompt.

        Parameters
        ----------
        image_path : str
            Relative path to the source image (e.g. ``"storage/uploads/abc.jpg"``).
        prompt : str
            Natural language description of the desired edit,
            e.g. ``"Change the sofa colour to dark navy blue"``.

        Returns
        -------
        str
            Relative path to the resulting edited image,
            e.g. ``"storage/edited/<uuid>.png"``.
            Currently returns MOCK DATA (a static sample path).

        Real Implementation (future)
        ----------------------------
            sam = SAM()
            mask = sam.segment(image_path)
            pipe = StableDiffusionInpaintPipeline.from_pretrained(...)
            result = pipe(prompt=prompt, image=img, mask_image=mask)
            result.images[0].save(output_path)
            return output_path
        """
        logger.debug(
            "[MOCK] ImageEditor.edit() called — image='%s', prompt='%s'",
            image_path,
            prompt,
        )

        # ── MOCK RESPONSE ─────────────────────────────────────────────────────
        mock_path = "storage/edited/sample.png"
        logger.info("[MOCK] Edited image path: %s", mock_path)
        return mock_path
