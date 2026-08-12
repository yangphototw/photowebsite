# Website Queue workflow

`Website_Queue` is your local drop area for website candidates. It is separate
from `public/images`, so you can choose photos without touching site code or
accidentally committing full-resolution files.

## Your workflow

1. Choose from a shoot's `8.AI_Pick` folder.
2. Copy one image to `cover/` and seven to eleven images to `gallery/` for a
   project. Keep the files as copies; do not move the original edited files.
3. For homepage assets, use the dedicated folders in `00_HOME`.
4. Tell Codex which category or project is ready to sync.

Codex will optimise the chosen files as WebP, generate thumbnails, update the
site's JSON data, test the build, and show you the result before deployment.

## Folder roles

| Folder | What to put there | Suggested amount |
| --- | --- | ---: |
| `00_HOME/hero` | Wide images with a clear subject and safe crop space | 2–4 |
| `00_HOME/featured` | Your strongest cross-category work | 8–12 |
| `00_HOME/cards/<category>` | One image representing that category | 1 |
| `<category>/<project>/cover` | The image that sells the project at a glance | 1 |
| `<category>/<project>/gallery` | A short visual story: opening, hero, emotion, detail, ending | 7–11 |

For hero images, avoid putting a face against the outer edge of the frame:
the site crops them differently on desktop and mobile. Category cards are
vertical (4:5), so choose a vertical image or one with generous crop space.

## Important rules

- Do not add photos directly to `public/images`.
- Do not rename source files merely for the website; the Queue folder identifies
  the intended placement.
- It is fine to copy the same photo into more than one Queue role when it is
  genuinely right for both, such as a project cover and homepage feature.
- The Queue is ignored by Git. It is a working area, not the published site.
