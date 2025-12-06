import shutil
import time
from pathlib import Path
from ultralytics import YOLO
import os

BASE = Path(__file__).parent
VIDEOS = BASE / 'videos'
OUT = BASE / 'outputs_ultralytics'
OUT.mkdir(exist_ok=True)

MODEL_NAME = 'yolov8n-pose.pt'

def list_videos():
    exts = {'.mp4', '.mov', '.avi', '.mkv'}
    return [p for p in VIDEOS.iterdir() if p.suffix.lower() in exts]

def find_latest_runs_predict():
    runs = list((BASE / 'runs' / 'predict').glob('**/*')) if (BASE / 'runs' / 'predict').exists() else []
    # find most recent directory under runs/predict
    base = BASE / 'runs' / 'predict'
    if not base.exists():
        return None
    dirs = [d for d in base.iterdir() if d.is_dir()]
    if not dirs:
        return None
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return dirs[0]

def process_video(path: Path):
    print('Processing (ultralytics):', path.name)
    model = YOLO(MODEL_NAME)
    # clear previous runs/predict to avoid mixing outputs
    runs_base = BASE / 'runs' / 'predict'
    if runs_base.exists():
        for d in runs_base.iterdir():
            try:
                if d.is_dir():
                    shutil.rmtree(d)
                else:
                    d.unlink()
            except Exception:
                pass

    # run prediction using streaming inference to avoid accumulating results in RAM
    results = model.predict(source=str(path), conf=0.25, save=True, device='cpu', stream=True)
    # iterate through the generator to ensure full processing
    for _ in results:
        pass

    # locate latest runs/predict folder
    out_dir = find_latest_runs_predict()
    if out_dir is None:
        print('Could not find runs/predict output for', path.name)
        return

    # move annotated video(s) to outputs_ultralytics
    moved = 0
    for f in out_dir.iterdir():
        if f.is_file() and f.suffix.lower() in {'.mp4', '.mov', '.avi'}:
            dest = OUT / f'annotated_{path.name}'
            shutil.move(str(f), str(dest))
            print('Moved', f.name, '->', dest)
            moved += 1
        elif f.is_file() and f.suffix.lower() in {'.jpg', '.png'}:
            dest = OUT / f'{path.stem}_{f.name}'
            shutil.move(str(f), str(dest))
    if moved == 0:
        # sometimes ultralytics saves images not video; try to create a video from images
        print('No direct annotated video found; copying all files from', out_dir)
        for f in out_dir.iterdir():
            if f.is_file():
                shutil.copy(str(f), str(OUT / f.name))

def main():
    videos = list_videos()
    if not videos:
        print('No videos found in', VIDEOS)
        return

    for v in videos:
        process_video(v)
        # small sleep to ensure runs folder timestamps differ
        time.sleep(1)

    print('Done. Annotated outputs:')
    for f in sorted(OUT.iterdir()):
        print('-', f.name)

if __name__ == '__main__':
    main()
