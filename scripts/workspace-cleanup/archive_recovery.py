#!/usr/bin/env python3
"""
Archive Recovery Tool
Quick recovery of archived files from pre-beta cleanup
"""

import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ArchiveRecoveryTool:
    """Tool for recovering files from cleanup archives"""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.archive_base = self.workspace_root / "archive"
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for recovery operations"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def find_cleanup_archives(self) -> List[Path]:
        """Find all available cleanup archives"""
        archives = []
        if self.archive_base.exists():
            for item in self.archive_base.iterdir():
                if item.is_dir() and item.name.startswith("pre-beta-cleanup-"):
                    archives.append(item)
        return sorted(archives, reverse=True)  # Most recent first

    def load_archive_metadata(self, archive_path: Path) -> Dict:
        """Load metadata for an archive"""
        metadata = {}

        # Walk through archive looking for metadata files
        for root, dirs, files in archive_path.rglob("*.metadata.json"):
            try:
                with open(root, "r") as f:
                    file_metadata = json.load(f)
                    original_path = file_metadata.get(
                        "original_path", "unknown"
                    )
                    metadata[original_path] = {
                        "metadata_file": root,
                        "archived_path": archive_path
                        / file_metadata.get("archived_path", ""),
                        "metadata": file_metadata,
                    }
            except Exception as e:
                self.logger.warning(
                    f"Failed to load metadata from {root}: {e}"
                )

        return metadata

    def search_archives(
        self, search_term: str, archive_path: Optional[Path] = None
    ) -> List[Dict]:
        """Search for files in archives"""
        results = []

        archives_to_search = (
            [archive_path] if archive_path else self.find_cleanup_archives()
        )

        for archive in archives_to_search:
            if not archive or not archive.exists():
                continue

            self.logger.info(f"Searching archive: {archive.name}")
            metadata = self.load_archive_metadata(archive)

            for original_path, info in metadata.items():
                if (
                    search_term.lower() in original_path.lower()
                    or search_term.lower()
                    in str(info["archived_path"]).lower()
                ):
                    results.append(
                        {
                            "original_path": original_path,
                            "archive": archive.name,
                            "archived_path": info["archived_path"],
                            "metadata": info["metadata"],
                        }
                    )

        return results

    def recover_file(
        self,
        original_path: str,
        archive_name: Optional[str] = None,
        destination: Optional[str] = None,
        dry_run: bool = True,
    ) -> bool:
        """Recover a specific file from archive"""

        # Find the file in archives
        search_results = self.search_archives(original_path)

        if not search_results:
            self.logger.error(
                f"File not found in any archive: {original_path}"
            )
            return False

        # Filter by archive name if specified
        if archive_name:
            search_results = [
                r for r in search_results if archive_name in r["archive"]
            ]

        if not search_results:
            self.logger.error(
                f"File not found in archive {archive_name}: {original_path}"
            )
            return False

        # Use most recent match
        match = search_results[0]

        # Determine destination
        if destination:
            dest_path = Path(destination)
        else:
            dest_path = self.workspace_root / match["original_path"]

        # Ensure destination directory exists
        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform recovery
        archived_file = Path(match["archived_path"])

        if not archived_file.exists():
            self.logger.error(f"Archived file not found: {archived_file}")
            return False

        self.logger.info(f"Recovering: {original_path}")
        self.logger.info(f"  From: {archived_file}")
        self.logger.info(f"  To: {dest_path}")

        if not dry_run:
            try:
                if archived_file.is_file():
                    shutil.copy2(archived_file, dest_path)
                else:
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(archived_file, dest_path)

                self.logger.info(f"✅ Successfully recovered: {original_path}")
                return True

            except Exception as e:
                self.logger.error(f"❌ Recovery failed: {e}")
                return False
        else:
            self.logger.info("🔍 DRY RUN - No files were actually recovered")
            return True

    def list_archived_files(
        self,
        archive_name: Optional[str] = None,
        category: Optional[str] = None,
    ):
        """List all archived files"""
        archives = self.find_cleanup_archives()

        if archive_name:
            archives = [a for a in archives if archive_name in a.name]

        for archive in archives:
            print(f"\n📁 Archive: {archive.name}")
            print(f"   Created: {archive.stat().st_mtime}")

            metadata = self.load_archive_metadata(archive)

            if category:
                # Filter by category
                filtered_metadata = {
                    k: v
                    for k, v in metadata.items()
                    if category.lower() in str(v["archived_path"]).lower()
                }
                metadata = filtered_metadata

            if not metadata:
                print("   (No matching files found)")
                continue

            for original_path, info in sorted(metadata.items()):
                file_metadata = info["metadata"]
                size = file_metadata.get("file_size", 0)
                size_str = self.format_file_size(size)
                file_type = file_metadata.get("file_type", "unknown")

                print(f"   📄 {original_path}")
                print(f"      Type: {file_type}, Size: {size_str}")
                print(
                    f"      Archived: {file_metadata.get('archived_date', 'unknown')}"
                )

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable form"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def emergency_restore_all(
        self, archive_name: str, dry_run: bool = True
    ) -> bool:
        """Emergency restore of entire archive (use with caution)"""

        archives = [
            a for a in self.find_cleanup_archives() if archive_name in a.name
        ]

        if not archives:
            self.logger.error(f"Archive not found: {archive_name}")
            return False

        archive = archives[0]

        print(f"🚨 EMERGENCY RESTORE from {archive.name}")
        print(
            "This will restore ALL archived files to their original locations."
        )
        print("Existing files may be overwritten!")

        if not dry_run:
            confirm = input(
                "Are you absolutely sure? Type 'RESTORE' to continue: "
            )
            if confirm != "RESTORE":
                print("Emergency restore cancelled.")
                return False

        metadata = self.load_archive_metadata(archive)
        restored_count = 0
        failed_count = 0

        for original_path, info in metadata.items():
            success = self.recover_file(
                original_path, archive_name, dry_run=dry_run
            )
            if success:
                restored_count += 1
            else:
                failed_count += 1

        print(f"\n✅ Emergency restore completed:")
        print(f"   Restored: {restored_count} files")
        print(f"   Failed: {failed_count} files")

        return failed_count == 0


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Archive Recovery Tool")
    parser.add_argument(
        "--workspace", default=".", help="Workspace root directory"
    )
    parser.add_argument(
        "--list", action="store_true", help="List archived files"
    )
    parser.add_argument("--search", help="Search for specific file")
    parser.add_argument("--recover", help="Recover specific file")
    parser.add_argument("--archive", help="Specific archive to work with")
    parser.add_argument(
        "--category", help="Filter by category (migration, debug, legacy)"
    )
    parser.add_argument(
        "--destination", help="Custom destination for recovery"
    )
    parser.add_argument(
        "--emergency-restore", help="Emergency restore entire archive"
    )
    parser.add_argument(
        "--live-run", action="store_true", help="Actually perform operations"
    )

    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    dry_run = not args.live_run

    recovery_tool = ArchiveRecoveryTool(workspace_root)

    if args.list:
        recovery_tool.list_archived_files(args.archive, args.category)
    elif args.search:
        results = recovery_tool.search_archives(args.search)
        if results:
            print(f"\n🔍 Found {len(results)} matches:")
            for result in results:
                print(f"   📄 {result['original_path']}")
                print(f"      Archive: {result['archive']}")
                print(
                    f"      Size: {recovery_tool.format_file_size(result['metadata'].get('file_size', 0))}"
                )
        else:
            print(f"❌ No matches found for: {args.search}")
    elif args.recover:
        recovery_tool.recover_file(
            args.recover, args.archive, args.destination, dry_run
        )
    elif args.emergency_restore:
        recovery_tool.emergency_restore_all(args.emergency_restore, dry_run)
    else:
        # Default: show available archives
        archives = recovery_tool.find_cleanup_archives()
        if archives:
            print("📚 Available cleanup archives:")
            for archive in archives:
                timestamp = datetime.fromtimestamp(archive.stat().st_mtime)
                print(
                    f"   📁 {archive.name} (Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
                )
            print(
                "\nUse --list to see archived files, --search to find specific files, or --recover to restore files."
            )
        else:
            print("❌ No cleanup archives found.")


if __name__ == "__main__":
    main()
