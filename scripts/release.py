from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT_DIR / "src" / "simpleautogui" / "_version.py"
VERSION_PATTERN = re.compile(r'(?P<prefix>__version__\s*=\s*")(?P<version>\d+\.\d+\.\d+)(?P<suffix>")')


class ReleaseError(RuntimeError):
    """Local release flow error."""


@dataclass(frozen=True, slots=True)
class ReleaseConfig:
    version_file: Path
    tag_prefix: str


class ReleaseService:
    """Bump package version, create release commit, and tag it."""

    def __init__(self, root_dir: Path, config: ReleaseConfig) -> None:
        self.root_dir = root_dir
        self.config = config

    def run(self, part: str, *, push: bool, dry_run: bool) -> str:
        current_version = self.get_current_version()
        next_version = self.bump_version(current_version, part)
        tag_name = f"{self.config.tag_prefix}{next_version}"

        print("Package: simpleautogui")
        print(f"Current version: {current_version}")
        print(f"Next version: {next_version}")
        print(f"Tag: {tag_name}")

        if dry_run:
            print("Dry run mode. No files or git objects were changed.")
            return next_version

        self.check_worktree_is_clean()
        self.check_tag_does_not_exist(tag_name)
        self.write_version(next_version)
        self.stage_version_file()
        self.git("commit", "-m", f"chore: release simpleautogui {tag_name}")
        self.git("tag", tag_name)

        if push:
            self.git("push")
            self.git("push", "origin", tag_name)
            print(f"Release {tag_name} was pushed.")
        else:
            print("Release commit and tag were created locally.")
            print("Run these commands when you are ready to publish:")
            print("  git push")
            print(f"  git push origin {tag_name}")

        return next_version

    def get_current_version(self) -> str:
        content = self.config.version_file.read_text(encoding="utf-8")
        match = VERSION_PATTERN.search(content)
        if match is None:
            raise ReleaseError(f"Version was not found in {self.config.version_file}.")
        return match.group("version")

    def write_version(self, version: str) -> None:
        content = self.config.version_file.read_text(encoding="utf-8")
        match = VERSION_PATTERN.search(content)
        if match is None:
            raise ReleaseError(f"Version was not found in {self.config.version_file}.")
        next_content = VERSION_PATTERN.sub(rf"\g<prefix>{version}\g<suffix>", content, count=1)
        self.config.version_file.write_text(next_content, encoding="utf-8")

    def stage_version_file(self) -> None:
        self.git("add", self.to_git_path(self.config.version_file))

    def bump_version(self, current_version: str, part: str) -> str:
        major, minor, patch = (int(item) for item in current_version.split("."))
        if part == "patch":
            patch += 1
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "major":
            major += 1
            minor = 0
            patch = 0
        else:
            raise ReleaseError(f"Unsupported release part: {part}.")
        return f"{major}.{minor}.{patch}"

    def check_worktree_is_clean(self) -> None:
        result = self.git("status", "--short", capture_output=True)
        if result.stdout.strip():
            raise ReleaseError("Git worktree is not clean. Commit or stash changes before release.")

    def check_tag_does_not_exist(self, tag_name: str) -> None:
        result = self.git(
            "rev-parse",
            "-q",
            "--verify",
            f"refs/tags/{tag_name}",
            check=False,
            capture_output=True,
        )
        if result.returncode == 0:
            raise ReleaseError(f"Git tag {tag_name} already exists.")

    def to_git_path(self, path: Path) -> str:
        return path.relative_to(self.root_dir).as_posix()

    def git(
            self,
            *args: str,
            check: bool = True,
            capture_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root_dir,
            check=check,
            text=True,
            capture_output=capture_output,
        )


class ReleaseCli:
    """CLI wrapper for the local release helper."""

    def __init__(self) -> None:
        self.service = ReleaseService(
            root_dir=ROOT_DIR,
            config=ReleaseConfig(
                version_file=VERSION_FILE,
                tag_prefix="v",
            ),
        )

    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Bump simpleautogui version and create a release tag.")
        parser.add_argument("part", choices=("patch", "minor", "major"))
        parser.add_argument("--push", action="store_true", help="Push commit and tag after local release.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show the next version without changing anything.",
        )
        return parser

    def main(self) -> int:
        parser = self.build_parser()
        args = parser.parse_args()

        try:
            self.service.run(args.part, push=args.push, dry_run=args.dry_run)
        except ReleaseError as exc:
            print(f"Release error: {exc}", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"Git command failed: {' '.join(exc.cmd)}", file=sys.stderr)
            return exc.returncode or 1

        return 0


if __name__ == "__main__":
    raise SystemExit(ReleaseCli().main())
