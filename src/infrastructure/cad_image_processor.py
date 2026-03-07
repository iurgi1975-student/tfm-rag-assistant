"""CADImageProcessor - Extract and process images from PDF and DXF files.

Handles:
- PDF: extracts embedded images with PyMuPDF (fitz)
- DXF: renders the drawing to PNG using ezdxf + matplotlib
- Thumbnail generation
- Basic text extraction from DXF title blocks
"""

import uuid
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image

from ..domain.models import ImageContent


class CADImageProcessor:
    """Extract images from PDF and DXF files and prepare ImageContent objects."""

    DEFAULT_OUTPUT_DIR = "./data/extracted_images"
    THUMBNAIL_SIZE = (256, 256)
    MIN_IMAGE_SIZE = 50  # pixels — skip tiny images (logos, bullets, etc.)

    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._thumb_dir = self.output_dir / "thumbnails"
        self._thumb_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_from_pdf(self, pdf_path: str) -> List[ImageContent]:
        """Extract all embedded images from a PDF.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            List of ImageContent objects (one per extracted image).
        """
        images: List[ImageContent] = []
        doc = fitz.open(pdf_path)

        for page_num, page in enumerate(doc):
            for img_index, img_info in enumerate(page.get_images(full=True)):
                xref = img_info[0]
                base_image = doc.extract_image(xref)

                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                if width < self.MIN_IMAGE_SIZE or height < self.MIN_IMAGE_SIZE:
                    continue

                image_id = str(uuid.uuid4())
                ext = base_image.get("ext", "png")
                image_filename = f"{image_id}.{ext}"
                image_path = str(self.output_dir / image_filename)

                with open(image_path, "wb") as f:
                    f.write(base_image["image"])

                thumbnail_path = self._create_thumbnail(image_path, image_id)

                images.append(ImageContent(
                    id=image_id,
                    image_path=image_path,
                    image_format=ext,
                    thumbnail_path=thumbnail_path,
                    width=width,
                    height=height,
                    extracted_text="",
                    metadata={
                        "source": pdf_path,
                        "page": page_num + 1,
                        "image_index": img_index,
                    }
                ))

        doc.close()
        return images

    def convert_dxf_to_image(self, dxf_path: str) -> Optional[ImageContent]:
        """Render a DXF file to a PNG image.

        Args:
            dxf_path: Path to the DXF file.

        Returns:
            ImageContent object or None if conversion fails.
        """
        try:
            import ezdxf
            from ezdxf.addons.drawing import RenderContext, Frontend
            from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
            import matplotlib.pyplot as plt

            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()

            fig = plt.figure(figsize=(16, 12), dpi=150)
            ax = fig.add_axes([0, 0, 1, 1])

            ctx = RenderContext(doc)
            backend = MatplotlibBackend(ax)
            Frontend(ctx, backend).draw_layout(msp)

            image_id = str(uuid.uuid4())
            image_path = str(self.output_dir / f"{image_id}.png")
            fig.savefig(image_path, format="png", bbox_inches="tight", dpi=150)
            plt.close(fig)

            with Image.open(image_path) as img:
                width, height = img.size

            thumbnail_path = self._create_thumbnail(image_path, image_id)
            extracted_text = self._extract_dxf_text(doc)

            return ImageContent(
                id=image_id,
                image_path=image_path,
                image_format="png",
                thumbnail_path=thumbnail_path,
                width=width,
                height=height,
                extracted_text=extracted_text,
                metadata={"source": dxf_path, "type": "dxf_render"}
            )

        except Exception as e:
            print(f"⚠️ DXF conversion failed for {dxf_path}: {e}")
            return None

    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = THUMBNAIL_SIZE) -> Optional[str]:
        """Public wrapper to create a thumbnail for an existing image.

        Args:
            image_path: Path to source image.
            size: Desired thumbnail size (width, height).

        Returns:
            Path to the thumbnail file, or None on failure.
        """
        image_id = Path(image_path).stem
        return self._create_thumbnail(image_path, image_id, size)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_thumbnail(
        self,
        image_path: str,
        image_id: str,
        size: Tuple[int, int] = THUMBNAIL_SIZE
    ) -> Optional[str]:
        """Create a thumbnail and return its path."""
        try:
            thumb_path = str(self._thumb_dir / f"{image_id}_thumb.png")
            with Image.open(image_path) as img:
                img.thumbnail(size, Image.LANCZOS)
                img.save(thumb_path, "PNG")
            return thumb_path
        except Exception:
            return None

    def _extract_dxf_text(self, doc) -> str:
        """Extract text entities from a DXF document (title block text, etc.)."""
        texts = []
        try:
            for entity in doc.modelspace():
                if entity.dxftype() in ("TEXT", "MTEXT"):
                    text_value = getattr(entity.dxf, "text", "") or getattr(entity.dxf, "insert", "")
                    if isinstance(text_value, str) and text_value.strip():
                        texts.append(text_value.strip())
        except Exception:
            pass
        return " | ".join(texts[:20])  # cap at 20 text blocks
