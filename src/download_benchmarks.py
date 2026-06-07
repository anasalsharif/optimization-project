from __future__ import annotations

from pathlib import Path
import subprocess


INSTANCE_URLS = {
    "c101_21.txt": "https://raw.githubusercontent.com/fwoerister/EVRPTW_Solver/master/problem_instances/c101_21.txt",
    "r101_21.txt": "https://raw.githubusercontent.com/fwoerister/EVRPTW_Solver/master/problem_instances/r101_21.txt",
    "rc103_21.txt": "https://raw.githubusercontent.com/fwoerister/EVRPTW_Solver/master/problem_instances/rc103_21.txt",
    "c101C5.txt": "https://raw.githubusercontent.com/fwoerister/EVRPTW_Solver/master/problem_instances/c101C5.txt",
}


def main() -> None:
    output_dir = Path("data") / "instances"
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in INSTANCE_URLS.items():
        target = output_dir / filename
        if not target.exists():
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"Invoke-WebRequest '{url}' -OutFile '{target}'",
                ],
                check=True,
            )
            print(f"Downloaded {filename}")
        else:
            print(f"Already present: {filename}")


if __name__ == "__main__":
    main()
