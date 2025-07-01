# video_index/encode_video.py
import subprocess
import sys
from typing import Optional
import argparse
from pathlib import Path

from .build_index import build_index


def encode_av1_intra(
    input_path: str,
    output_path: str,
    crf: int = 30,
    cpu_used: int = 4,
    tune: Optional[str] = None,
) -> None:
    """
    Encode a video to AV1 intra-only IVF format using FFmpeg and libaom-av1.

    Parameters
    ----------
    input_path : str
        Path to the input video file.
    output_path : str
        Path to save the encoded AV1 IVF video.
    crf : int, optional
        Constant Rate Factor for quality (lower is better quality), by default 30
    cpu_used : int, optional
        Speed/quality tradeoff, lower is slower/better, by default 4
    tune : Optional[str], optional
        Tune preset string for encoder (e.g., 'psnr'), by default None

    Raises
    ------
    RuntimeError
        If the encoding process fails.
    """
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", input_path,
        "-c:v", "libaom-av1",
        "-g", "1",  # GOP size 1 = intra-only
        "-cpu-used", str(cpu_used),
        "-crf", str(crf),
        "-row-mt", "1",  # enable row-based multi-threading for speed
        "-tile-columns", "0",  # single tile for intra-only
        "-f", "ivf",
        output_path,
    ]

    if tune:
        ffmpeg_cmd.extend(["-tune", tune])

    print("Running ffmpeg:", " ".join(ffmpeg_cmd))
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg encoding failed with code {result.returncode}:\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Encode video to AV1 intra-only IVF and optionally build frame index."
    )
    parser.add_argument("input", help="Input video path")
    parser.add_argument("output", help="Output IVF video path")
    parser.add_argument(
        "--crf", type=int, default=30, help="Constant Rate Factor (quality, lower better)"
    )
    parser.add_argument(
        "--cpu-used",
        type=int,
        default=4,
        help="CPU usage level for encoder speed/quality tradeoff (0-8)",
    )
    parser.add_argument(
        "--tune", default=None, help="Tune preset for encoder (e.g., psnr)"
    )
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build the 128-bit frame index file after encoding",
    )

    args = parser.parse_args()

    encode_av1_intra(args.input, args.output, args.crf, args.cpu_used, args.tune)

    if args.build_index:
        index_path = Path(args.output).with_suffix(args.output.suffix + ".idx")
        print(f"Building index at {index_path}")
        build_index(args.output, str(index_path))


if __name__ == "__main__":
    '''
    python -m video_index.encode_video input.mp4 output.ivf --crf 28 --cpu-used 4 --build-index
    '''
    
    main()

