"""Create the local Website Queue and seed it from the currently published site.

Run from the website root after a fresh move. Existing files are left intact,
so it is safe to run again after new project folders have been added manually.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "Website_Queue"
PUBLIC = ROOT / "public"
DATA = ROOT / "src" / "data"

CATEGORIES = (
    ("01_WEDDING", "wedding", "Wedding / 婚禮"),
    ("02_REGISTRATION", "registration", "Registration / 登記"),
    ("03_PORTRAIT", "portrait", "Portrait / 人像"),
    ("04_TRAVEL", "travel", "Travel / 旅遊"),
    ("05_PRODUCT", "product", "Product / 商品"),
    ("06_EVENT", "event", "Event / 活動紀錄"),
    ("07_ABOUT", "about", "About / 關於"),
)


def read_json(name: str):
    path = DATA / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def safe_name(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "-", value).strip(" .")
    return cleaned or "untitled-project"


def ensure_readme(directory: Path, content: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    readme = directory / "README.md"
    if not readme.exists():
        readme.write_text(content.strip() + "\n", encoding="utf-8")


def copy_public_asset(src: str, destination: Path, manifest: list[dict], role: str) -> None:
    source = PUBLIC / src.lstrip("/")
    if not source.is_file():
        raise FileNotFoundError(f"Published asset is missing: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / source.name
    if not target.exists():
        shutil.copy2(source, target)
    manifest.append({"role": role, "source": src, "queue_file": str(target.relative_to(QUEUE))})


def category_folder(category_slug: str) -> Path:
    for folder, slug, _ in CATEGORIES:
        if slug == category_slug:
            return QUEUE / folder
    return QUEUE / f"99_{safe_name(category_slug).upper()}"


def main() -> None:
    manifest: list[dict] = []
    ensure_readme(
        QUEUE,
        "# Website Queue\n\nDrop selected images into this folder structure. "
        "Read `../docs/WEBSITE_QUEUE.md` before adding a new project.",
    )

    home = QUEUE / "00_HOME"
    ensure_readme(home, "# Home page\n\nUse the role folders below. Do not mix project galleries here.")
    for name, note in (
        ("hero", "# Hero\n\n2–4 wide images. Keep faces away from the outer crop edges."),
        ("featured", "# Featured\n\n8–12 strongest cross-category images."),
        ("cards", "# Category cards\n\nOne representative image per category; vertical crop works best."),
    ):
        ensure_readme(home / name, note)

    for folder, slug, title in CATEGORIES:
        category = QUEUE / folder
        ensure_readme(category, f"# {title}\n\nCreate one folder per website project. Each project needs `cover` and `gallery`.")
        if slug != "about":
            ensure_readme(home / "cards" / slug, f"# {title} card\n\nKeep exactly one category-card candidate here.")

    carousel = read_json("carousel.json")
    cards = read_json("cards.json")
    albums = read_json("albums.json")
    about = read_json("about.json")

    for item in carousel:
        copy_public_asset(item["src"], home / "hero", manifest, "home-hero-current")
    for item in cards:
        copy_public_asset(item["src"], home / "cards" / item["category"], manifest, "home-card-current")
    if about.get("profileSrc"):
        profile = QUEUE / "07_ABOUT" / "profile"
        ensure_readme(profile, "# Profile\n\nOne or two photographer profile images for the About page.")
        copy_public_asset(about["profileSrc"], profile, manifest, "about-profile-current")

    all_images = [image for album in albums for image in album.get("images", [])]
    for image in all_images[8:32]:
        copy_public_asset(image["src"], home / "featured", manifest, "home-featured-current-fallback")

    for album in albums:
        category = category_folder(album["categorySlug"])
        project_name = "00_CURRENT_GALLERY" if album["projectSlug"] == "gallery" else safe_name(album["projectSlug"])
        project = category / project_name
        cover = project / "cover"
        gallery = project / "gallery"
        ensure_readme(project, "# Project\n\nPut one image in `cover` and seven to eleven images in `gallery`.")
        ensure_readme(cover, "# Cover\n\nOne image that represents this project at a glance.")
        ensure_readme(gallery, "# Gallery\n\nA concise story: opening, hero, interaction, detail, and ending.")
        copy_public_asset(album["cover"], cover, manifest, "project-cover-current")
        for image in album.get("images", []):
            copy_public_asset(image["src"], gallery, manifest, "project-gallery-current")

    (QUEUE / ".current-site-seed.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Website Queue ready: {QUEUE}")
    print(f"Seeded {len(manifest)} references from the current published assets.")


if __name__ == "__main__":
    main()
