import asyncio
import json
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../video_analysis_bot"))

from video_analysis_bot.db import init_db, close_db
from video_analysis_bot.db.models import Video, VideoSnapshot


async def load_data(file_path: str):
    print(f"Loading data from {file_path}...")

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    await init_db()

    videos_data = data.get("videos", [])
    print(f"Found {len(videos_data)} videos to process.")

    for video_data in videos_data:
        # Extract snapshots data
        snapshots_data = video_data.pop("snapshots", [])

        # Create or update Video
        video, created = await Video.update_or_create(
            id=video_data["id"], defaults=video_data
        )

        action = "Created" if created else "Updated"
        # print(f"{action} Video: {video.id}")

        # Create Snapshots
        # For bulk creating, we can prepare a list.
        # However, update_or_create is safer if re-running script.
        # Given the volume, bulk_create is faster if we assume fresh start,
        # but let's use update_or_create for safety or bulk_create with ignore_conflicts if supported (Tortoise specific)

        # For this task, simple iteration is fine unless dataset is massive.
        # The user mentioned "large volume" so bulk_create is better.
        # But we need to handle potential duplicates if script runs twice.
        # Let's try to fetch existing IDs first or just use update_or_create for robustness.

        for snapshot_data in snapshots_data:
            snapshot_data["video_id"] = video.id
            await VideoSnapshot.update_or_create(
                id=snapshot_data["id"], defaults=snapshot_data
            )

    print("Data loading completed.")
    await close_db()


if __name__ == "__main__":
    # Default to videos.json, but allow argument
    json_file = "videos.json"
    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    asyncio.run(load_data(json_file))
