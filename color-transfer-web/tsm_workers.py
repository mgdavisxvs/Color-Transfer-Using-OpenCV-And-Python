"""
TSM Color Transfer Workers

This module implements specialized color transfer workers using the
Tom Sawyer Method framework. Each worker uses a different variation
of the color transfer algorithm for ensemble intelligence.
"""

import sys
from pathlib import Path
import numpy as np
import cv2
from typing import Any, Dict, Tuple

# Import TSM framework
sys.path.insert(0, str(Path(__file__).parent.parent / 'tom-sawyer-method'))
from tsm.core.worker import Worker, WorkerConfig
from tsm.core.result import WorkerResult


class ColorTransferWorkerBase(Worker):
    """Base class for color transfer workers."""

    def __init__(self, worker_id: str, config: WorkerConfig):
        super().__init__(worker_id, config)
        self.epsilon = config.parameters.get('epsilon', 1e-10)

    def _convert_to_lab(self, image: np.ndarray) -> np.ndarray:
        """Convert image to LAB color space."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype("float32")

    def _convert_to_bgr(self, image: np.ndarray) -> np.ndarray:
        """Convert image back to BGR color space."""
        return cv2.cvtColor(image.astype("uint8"), cv2.COLOR_LAB2BGR)

    def _compute_stats(self, image: np.ndarray) -> Tuple:
        """Compute channel statistics."""
        l, a, b = cv2.split(image)
        return (l.mean(), l.std(), a.mean(), a.std(), b.mean(), b.std())


class StandardColorTransferWorker(ColorTransferWorkerBase):
    """
    Standard color transfer worker using basic LAB statistics.

    This is the baseline implementation using mean and standard deviation
    matching in LAB color space.
    """

    def process(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Perform standard color transfer.

        Args:
            data: Dictionary with 'source' and 'target' images

        Returns:
            Transferred image
        """
        source = data['source']
        target = data['target']

        # Convert to LAB
        source_lab = self._convert_to_lab(source)
        target_lab = self._convert_to_lab(target)

        # Compute statistics
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._compute_stats(source_lab)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self._compute_stats(target_lab)

        # Split target channels
        l, a, b = cv2.split(target_lab)

        # Transfer statistics
        l = (l - lMeanTar) * (lStdSrc / (lStdTar + self.epsilon)) + lMeanSrc
        a = (a - aMeanTar) * (aStdSrc / (aStdTar + self.epsilon)) + aMeanSrc
        b = (b - bMeanTar) * (bStdSrc / (bStdTar + self.epsilon)) + bMeanSrc

        # Clip values
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Merge and convert back
        result = cv2.merge([l, a, b])
        return self._convert_to_bgr(result)

    def get_confidence(self, data: Dict[str, np.ndarray], result: np.ndarray) -> float:
        """Calculate confidence based on color distribution similarity."""
        source_lab = self._convert_to_lab(data['source'])
        result_lab = self._convert_to_lab(result)

        # Compare color distributions
        source_stats = self._compute_stats(source_lab)
        result_stats = self._compute_stats(result_lab)

        # Calculate similarity (inverse of normalized difference)
        differences = []
        for i in range(len(source_stats)):
            if source_stats[i] != 0:
                diff = abs(source_stats[i] - result_stats[i]) / abs(source_stats[i])
                differences.append(diff)

        avg_diff = np.mean(differences)
        confidence = max(0.0, min(1.0, 1.0 - avg_diff))

        return confidence


class LuminancePreservingWorker(ColorTransferWorkerBase):
    """
    Luminance-preserving color transfer worker.

    This worker transfers color (a, b channels) while preserving
    the original luminance (L channel) of the target image.
    """

    def process(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Perform luminance-preserving color transfer."""
        source = data['source']
        target = data['target']

        # Convert to LAB
        source_lab = self._convert_to_lab(source)
        target_lab = self._convert_to_lab(target)

        # Compute statistics
        (_, _, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._compute_stats(source_lab)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self._compute_stats(target_lab)

        # Split target channels
        l, a, b = cv2.split(target_lab)

        # Preserve L channel, only transfer a and b
        # Apply slight adjustment to L for consistency
        l = l * 0.95 + lMeanTar * 0.05  # Minimal L adjustment

        # Transfer color channels
        a = (a - aMeanTar) * (aStdSrc / (aStdTar + self.epsilon)) + aMeanSrc
        b = (b - bMeanTar) * (bStdSrc / (bStdTar + self.epsilon)) + bMeanSrc

        # Clip values
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Merge and convert back
        result = cv2.merge([l, a, b])
        return self._convert_to_bgr(result)

    def get_confidence(self, data: Dict[str, np.ndarray], result: np.ndarray) -> float:
        """Higher confidence as this method is more conservative."""
        return 0.85  # High confidence due to luminance preservation


class AdaptiveColorTransferWorker(ColorTransferWorkerBase):
    """
    Adaptive color transfer worker with local adjustments.

    This worker applies color transfer adaptively based on local
    image characteristics, providing better results for complex images.
    """

    def process(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Perform adaptive color transfer."""
        source = data['source']
        target = data['target']

        # Convert to LAB
        source_lab = self._convert_to_lab(source)
        target_lab = self._convert_to_lab(target)

        # Global statistics
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._compute_stats(source_lab)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self._compute_stats(target_lab)

        # Split target channels
        l, a, b = cv2.split(target_lab)

        # Adaptive weight based on local variance
        # Higher variance areas get more aggressive transfer
        local_variance = cv2.GaussianBlur(l, (15, 15), 0)
        local_variance = (local_variance - local_variance.min()) / (local_variance.max() - local_variance.min() + self.epsilon)

        # Apply adaptive transfer
        l_transferred = (l - lMeanTar) * (lStdSrc / (lStdTar + self.epsilon)) + lMeanSrc
        a_transferred = (a - aMeanTar) * (aStdSrc / (aStdTar + self.epsilon)) + aMeanSrc
        b_transferred = (b - bMeanTar) * (bStdSrc / (bStdTar + self.epsilon)) + bMeanSrc

        # Blend based on local characteristics
        alpha = 0.7 + 0.3 * local_variance  # Adaptive blending
        l = l * (1 - alpha) + l_transferred * alpha
        a = a_transferred  # Full transfer for color channels
        b = b_transferred

        # Clip values
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Merge and convert back
        result = cv2.merge([l, a, b])
        return self._convert_to_bgr(result)

    def get_confidence(self, data: Dict[str, np.ndarray], result: np.ndarray) -> float:
        """Confidence based on image complexity."""
        target = data['target']
        gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

        # Calculate image complexity (edge density)
        edges = cv2.Canny(gray, 50, 150)
        complexity = np.sum(edges > 0) / edges.size

        # Higher confidence for complex images
        confidence = 0.7 + 0.3 * min(complexity * 10, 1.0)
        return confidence


class MedianFilteredWorker(ColorTransferWorkerBase):
    """
    Median-filtered color transfer worker.

    This worker applies median filtering to reduce noise and
    produce smoother color transitions.
    """

    def process(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Perform color transfer with median filtering."""
        source = data['source']
        target = data['target']

        # Convert to LAB
        source_lab = self._convert_to_lab(source)
        target_lab = self._convert_to_lab(target)

        # Apply median filter to reduce noise
        source_lab = cv2.medianBlur(source_lab, 3)
        target_lab = cv2.medianBlur(target_lab, 3)

        # Compute statistics
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._compute_stats(source_lab)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self._compute_stats(target_lab)

        # Split target channels
        l, a, b = cv2.split(target_lab)

        # Transfer statistics
        l = (l - lMeanTar) * (lStdSrc / (lStdTar + self.epsilon)) + lMeanSrc
        a = (a - aMeanTar) * (aStdSrc / (aStdTar + self.epsilon)) + aMeanSrc
        b = (b - bMeanTar) * (bStdSrc / (bStdTar + self.epsilon)) + bMeanSrc

        # Clip values
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Merge and convert back
        result = cv2.merge([l, a, b])
        return self._convert_to_bgr(result)

    def get_confidence(self, data: Dict[str, np.ndarray], result: np.ndarray) -> float:
        """Good confidence for smooth results."""
        return 0.80


class IntensityScaledWorker(ColorTransferWorkerBase):
    """
    Intensity-scaled color transfer worker.

    This worker scales the transfer intensity based on a configurable
    parameter, allowing for subtle to aggressive transfers.
    """

    def process(self, data: Dict[str, np.ndarray]) -> np.ndarray:
        """Perform intensity-scaled color transfer."""
        source = data['source']
        target = data['target']

        # Get intensity scale from config
        intensity = self.config.parameters.get('intensity', 1.0)

        # Convert to LAB
        source_lab = self._convert_to_lab(source)
        target_lab = self._convert_to_lab(target)

        # Compute statistics
        (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = self._compute_stats(source_lab)
        (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = self._compute_stats(target_lab)

        # Split target channels
        l, a, b = cv2.split(target_lab)

        # Transfer with intensity scaling
        l_transfer = (l - lMeanTar) * (lStdSrc / (lStdTar + self.epsilon)) + lMeanSrc
        a_transfer = (a - aMeanTar) * (aStdSrc / (aStdTar + self.epsilon)) + aMeanSrc
        b_transfer = (b - bMeanTar) * (bStdSrc / (bStdTar + self.epsilon)) + bMeanSrc

        # Blend based on intensity
        l = l * (1 - intensity) + l_transfer * intensity
        a = a * (1 - intensity) + a_transfer * intensity
        b = b * (1 - intensity) + b_transfer * intensity

        # Clip values
        l = np.clip(l, 0, 255)
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)

        # Merge and convert back
        result = cv2.merge([l, a, b])
        return self._convert_to_bgr(result)

    def get_confidence(self, data: Dict[str, np.ndarray], result: np.ndarray) -> float:
        """Confidence based on intensity parameter."""
        intensity = self.config.parameters.get('intensity', 1.0)
        # Lower intensity = higher confidence (more conservative)
        confidence = 0.6 + 0.3 * (1.0 - abs(intensity - 0.5) * 2)
        return confidence


def create_color_transfer_workers() -> list:
    """
    Create a suite of color transfer workers for TSM.

    Returns:
        List of configured Worker instances
    """
    workers = []

    # Standard worker
    workers.append(StandardColorTransferWorker(
        worker_id="standard_transfer",
        config=WorkerConfig(
            worker_id="standard_transfer",
            worker_type="StandardColorTransferWorker",
            parameters={'epsilon': 1e-10}
        )
    ))

    # Luminance preserving worker
    workers.append(LuminancePreservingWorker(
        worker_id="luminance_preserving",
        config=WorkerConfig(
            worker_id="luminance_preserving",
            worker_type="LuminancePreservingWorker",
            parameters={'epsilon': 1e-10}
        )
    ))

    # Adaptive worker
    workers.append(AdaptiveColorTransferWorker(
        worker_id="adaptive_transfer",
        config=WorkerConfig(
            worker_id="adaptive_transfer",
            worker_type="AdaptiveColorTransferWorker",
            parameters={'epsilon': 1e-10}
        )
    ))

    # Median filtered worker
    workers.append(MedianFilteredWorker(
        worker_id="median_filtered",
        config=WorkerConfig(
            worker_id="median_filtered",
            worker_type="MedianFilteredWorker",
            parameters={'epsilon': 1e-10}
        )
    ))

    # Intensity scaled workers (different intensities)
    for intensity in [0.7, 0.9, 1.2]:
        worker_id = f"intensity_{int(intensity * 100)}"
        workers.append(IntensityScaledWorker(
            worker_id=worker_id,
            config=WorkerConfig(
                worker_id=worker_id,
                worker_type="IntensityScaledWorker",
                parameters={'epsilon': 1e-10, 'intensity': intensity}
            )
        ))

    return workers
