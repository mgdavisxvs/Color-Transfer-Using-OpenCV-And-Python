#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Color Transfer Algorithm

This module implements color transfer between images using LAB color space
statistics, based on the method described in Reinhard et al. (2001).

Example:
    $ python algorithm_improved.py --source source.jpg --target target.jpg --output result.png
"""

import argparse
import logging
import os
from pathlib import Path
from typing import Tuple

import cv2
import imutils
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DISPLAY_HEIGHT = 400
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
DEFAULT_MAX_DIMENSION = 4000
EPSILON = 1e-10
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


def validate_image_path(path_str: str) -> Path:
    """
    Validate and sanitize image file path.

    Args:
        path_str: Path string to validate

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type invalid or file too large
    """
    try:
        path = Path(path_str).resolve()
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid path: {path_str}") from e

    # Check if file exists
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    # Check extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type '{path.suffix}'. "
            f"Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check file size (prevent memory exhaustion)
    file_size = path.stat().st_size
    if file_size > DEFAULT_MAX_FILE_SIZE:
        raise ValueError(
            f"File too large ({file_size / 1024 / 1024:.1f}MB). "
            f"Max size: {DEFAULT_MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )

    return path


def load_image(path: Path) -> np.ndarray:
    """
    Load and validate image from file.

    Args:
        path: Path to image file

    Returns:
        Image as numpy array in BGR format

    Raises:
        ValueError: If image cannot be loaded or is invalid
    """
    logger.info(f"Loading image: {path}")
    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(f"Failed to load image: {path}")

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError(
            f"Invalid image format. Expected 3-channel image, "
            f"got shape: {image.shape}"
        )

    logger.info(f"Image loaded: {image.shape[1]}x{image.shape[0]}")
    return image


def resize_if_needed(image: np.ndarray, max_dimension: int = DEFAULT_MAX_DIMENSION) -> np.ndarray:
    """
    Resize image if dimensions exceed maximum.

    Args:
        image: Input image
        max_dimension: Maximum allowed dimension

    Returns:
        Resized image if needed, otherwise original image
    """
    height, width = image.shape[:2]

    if max(height, width) > max_dimension:
        scale = max_dimension / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)

        logger.info(
            f"Resizing image from {width}x{height} to {new_width}x{new_height}"
        )

        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return image


def image_stats(image: np.ndarray) -> Tuple[float, float, float, float, float, float]:
    """
    Compute color statistics for LAB image.

    Args:
        image: Image in LAB color space (float32)

    Returns:
        Tuple of (lMean, lStd, aMean, aStd, bMean, bStd)
    """
    # Split channels
    channels = cv2.split(image)

    # Compute statistics for each channel
    stats = []
    for channel in channels:
        stats.append(channel.mean())
        stats.append(channel.std())

    return tuple(stats)


def color_transfer(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """
    Transfer color scheme from source image to target image.

    Uses LAB color space statistics to match the color distribution
    of the target image to the source image. This implementation is based
    on the algorithm described in:

    Reinhard et al. "Color Transfer between Images" (2001)

    Args:
        source: Source image in BGR format (H, W, 3)
        target: Target image in BGR format (H, W, 3)

    Returns:
        Transferred image in BGR format (H, W, 3)

    Raises:
        ValueError: If images have invalid shapes or types
    """
    # Validate inputs
    if source is None or target is None:
        raise ValueError("Source and target images cannot be None")

    if len(source.shape) != 3 or len(target.shape) != 3:
        raise ValueError("Images must be 3-dimensional (H, W, C)")

    if source.shape[2] != 3 or target.shape[2] != 3:
        raise ValueError("Images must have 3 channels")

    logger.info("Starting color transfer...")

    # Convert images from BGR to LAB color space
    # Using float32 as required by OpenCV
    source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype("float32")
    target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype("float32")

    # Compute color statistics for source and target images
    (lMeanSrc, lStdSrc, aMeanSrc, aStdSrc, bMeanSrc, bStdSrc) = image_stats(source_lab)
    (lMeanTar, lStdTar, aMeanTar, aStdTar, bMeanTar, bStdTar) = image_stats(target_lab)

    logger.debug(f"Source stats - L: {lMeanSrc:.2f}±{lStdSrc:.2f}, "
                f"a: {aMeanSrc:.2f}±{aStdSrc:.2f}, b: {bMeanSrc:.2f}±{bStdSrc:.2f}")
    logger.debug(f"Target stats - L: {lMeanTar:.2f}±{lStdTar:.2f}, "
                f"a: {aMeanTar:.2f}±{aStdTar:.2f}, b: {bMeanTar:.2f}±{bStdTar:.2f}")

    # Split target image into LAB channels
    (l, a, b) = cv2.split(target_lab)

    # Subtract the means from the target image
    l -= lMeanTar
    a -= aMeanTar
    b -= bMeanTar

    # Scale by the standard deviations (with epsilon to prevent division by zero)
    l *= (lStdTar / (lStdSrc + EPSILON))
    a *= (aStdTar / (aStdSrc + EPSILON))
    b *= (bStdTar / (bStdSrc + EPSILON))

    # Add in the source mean
    l += lMeanSrc
    a += aMeanSrc
    b += bMeanSrc

    # Clip pixel intensities to [0, 255] to ensure valid range
    l = np.clip(l, 0, 255)
    a = np.clip(a, 0, 255)
    b = np.clip(b, 0, 255)

    # Merge channels and convert back to BGR color space
    transfer = cv2.merge([l, a, b])
    transfer = cv2.cvtColor(transfer.astype("uint8"), cv2.COLOR_LAB2BGR)

    logger.info("Color transfer completed successfully")
    return transfer


def save_image(image: np.ndarray, output_path: str) -> None:
    """
    Save image to file.

    Args:
        image: Image to save
        output_path: Path where image should be saved

    Raises:
        IOError: If image cannot be saved
    """
    logger.info(f"Saving result to: {output_path}")

    success = cv2.imwrite(output_path, image)

    if not success:
        raise IOError(f"Failed to save image to: {output_path}")

    logger.info("Image saved successfully")


def display_results(source: np.ndarray, target: np.ndarray,
                   transfer: np.ndarray, display_height: int = DEFAULT_DISPLAY_HEIGHT) -> None:
    """
    Display source, target, and transferred images side by side.

    Args:
        source: Source image
        target: Target image
        transfer: Transferred image
        display_height: Height for display (images will be resized)
    """
    logger.info("Displaying results...")

    # Resize images for display
    source_display = imutils.resize(source, height=display_height)
    target_display = imutils.resize(target, height=display_height)
    transfer_display = imutils.resize(transfer, height=display_height)

    # Stack horizontally
    combined = np.hstack([source_display, target_display, transfer_display])

    # Display
    cv2.imshow("Color Transfer - Source | Target | Result", combined)
    logger.info("Press any key to close the window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Transfer color scheme from source image to target image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--source",
        required=True,
        help="Path to source image file"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Path to target image file"
    )

    parser.add_argument(
        "--output",
        help="Path to save the result (optional)"
    )

    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Don't display the result window"
    )

    parser.add_argument(
        "--display-height",
        type=int,
        default=DEFAULT_DISPLAY_HEIGHT,
        help="Height for display images"
    )

    parser.add_argument(
        "--max-dimension",
        type=int,
        default=DEFAULT_MAX_DIMENSION,
        help="Maximum image dimension for processing (images will be resized if larger)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main function to run color transfer from command line.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Parse arguments
        args = parse_arguments()

        # Set logging level
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        # Validate and load images
        source_path = validate_image_path(args.source)
        target_path = validate_image_path(args.target)

        source = load_image(source_path)
        target = load_image(target_path)

        # Resize if needed to prevent memory issues
        source = resize_if_needed(source, args.max_dimension)
        target = resize_if_needed(target, args.max_dimension)

        # Perform color transfer
        transfer = color_transfer(source, target)

        # Save result if output path specified
        if args.output:
            save_image(transfer, args.output)

        # Display results unless disabled
        if not args.no_display:
            display_results(source, target, transfer, args.display_height)

        logger.info("Process completed successfully")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return 1

    except IOError as e:
        logger.error(f"I/O error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 130

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
