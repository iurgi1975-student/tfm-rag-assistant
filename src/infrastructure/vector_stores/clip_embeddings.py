"""CLIPEmbeddings - Multimodal embeddings using CLIP via sentence-transformers.

Embeds both text and images into the same 512-dimensional vector space,
enabling cross-modal similarity search (find images with a text query and vice-versa).
"""

import os
import warnings
from typing import List, Optional
from pathlib import Path

# Suppress the HuggingFace tokenizer warning about sequence length > max_seq_length.
# sentence-transformers sets max_seq_length=77 and truncates correctly, but the
# underlying HF tokenizer fires the warning BEFORE applying truncation.
warnings.filterwarnings(
    "ignore",
    message=r"Token indices sequence length is longer than the specified maximum",
    category=UserWarning,
)

# Limit OpenBLAS/OMP threads to avoid OOM on low-RAM systems (~12 GB)
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import torch
from PIL import Image

# Local copy of the model (real files, no symlinks)
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_LOCAL_MODEL_DIR = str(_PROJECT_ROOT / "models" / "clip" / "clip-ViT-B-32-local")

from sentence_transformers import SentenceTransformer


class CLIPEmbeddings:
    """CLIP-based embeddings for text and images.

    Uses the clip-ViT-B-32 model from sentence-transformers.
    Both text and image embeddings live in the same 512-dim space,
    so you can search images using a text query and vice-versa.

    The model is loaded lazily on first use so the app starts instantly.
    """

    EMBEDDING_DIM = 512

    def __init__(self, model_name: str = "clip-ViT-B-32"):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model_name = model_name
        self._model: Optional[SentenceTransformer] = None  # loaded on first use

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            print(f"📦 Loading CLIP model from {_LOCAL_MODEL_DIR} ...", flush=True)
            self._model = SentenceTransformer(_LOCAL_MODEL_DIR, device=self._device)
            # CLIP hard limit: 77 tokens. Set on both sentence-transformers and the
            # underlying HF tokenizer so truncation happens silently before the warning fires.
            self._model.max_seq_length = 77
            try:
                self._model[0].tokenizer.model_max_length = 77
            except Exception:
                pass
            print(f"✅ CLIP model ready on {self._device}", flush=True)
        return self._model

    # DXF text with numbers/±/°/symbols tokenizes to ~1.2 chars/token on average,
    # so 100 chars ≈ 83 tokens — safely within CLIP's 77-token limit after HF truncation.
    _MAX_TEXT_CHARS = 100

    @staticmethod
    def _truncate(texts: List[str]) -> List[str]:
        return [t[:CLIPEmbeddings._MAX_TEXT_CHARS] for t in texts]

    # ------------------------------------------------------------------
    # Text embeddings (LangChain-compatible interface)
    # ------------------------------------------------------------------

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            List of 512-dimensional float vectors.
        """
        embeddings = self._get_model().encode(
            self._truncate(texts), convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string.

        Args:
            text: Query string.

        Returns:
            512-dimensional float vector.
        """
        embedding = self._get_model().encode(
            text[:self._MAX_TEXT_CHARS], convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True
        )
        return embedding.tolist()

    # ------------------------------------------------------------------
    # Image embeddings
    # ------------------------------------------------------------------

    def embed_image(self, image_path: str) -> List[float]:
        """Embed a single image file.

        Args:
            image_path: Path to the image file (PNG, JPG, etc.).

        Returns:
            512-dimensional float vector.
        """
        image = Image.open(image_path).convert("RGB")
        embedding = self._get_model().encode(image, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()

    def embed_images(self, image_paths: List[str]) -> List[List[float]]:
        """Embed a list of image files.

        Args:
            image_paths: List of paths to image files.

        Returns:
            List of 512-dimensional float vectors.
        """
        images = [Image.open(p).convert("RGB") for p in image_paths]
        embeddings = self._get_model().encode(images, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
