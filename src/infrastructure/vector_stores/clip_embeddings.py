"""CLIPEmbeddings - Multimodal embeddings using CLIP via sentence-transformers.

Embeds both text and images into the same 512-dimensional vector space,
enabling cross-modal similarity search (find images with a text query and vice-versa).
"""

from typing import List
from pathlib import Path

import torch
from PIL import Image
from sentence_transformers import SentenceTransformer


class CLIPEmbeddings:
    """CLIP-based embeddings for text and images.

    Uses the clip-ViT-B-32 model from sentence-transformers.
    Both text and image embeddings live in the same 512-dim space,
    so you can search images using a text query and vice-versa.
    """

    EMBEDDING_DIM = 512

    def __init__(self, model_name: str = "clip-ViT-B-32"):
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = SentenceTransformer(model_name, device=self._device)

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
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string.

        Args:
            text: Query string.

        Returns:
            512-dimensional float vector.
        """
        embedding = self._model.encode(text, convert_to_numpy=True, show_progress_bar=False)
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
        embedding = self._model.encode(image, convert_to_numpy=True, show_progress_bar=False)
        return embedding.tolist()

    def embed_images(self, image_paths: List[str]) -> List[List[float]]:
        """Embed a list of image files.

        Args:
            image_paths: List of paths to image files.

        Returns:
            List of 512-dimensional float vectors.
        """
        images = [Image.open(p).convert("RGB") for p in image_paths]
        embeddings = self._model.encode(images, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
