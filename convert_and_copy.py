import cv2
from pathlib import Path
import shutil

BASE = Path(__file__).parent
IN_DIR = BASE / 'outputs_ultralytics'
VID_DIR = BASE / 'videos'
IMG_DIR = BASE / 'images'
VID_DIR.mkdir(exist_ok=True)
IMG_DIR.mkdir(exist_ok=True)

def convert_avi_to_mp4(src: Path, dest: Path):
    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        print('Failed to open', src)
        return False
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(dest), fourcc, fps, (w, h))
    frame_count = 0
    success = True
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
        if frame_count == 0:
            # save first frame as thumbnail
            thumb = IMG_DIR / (dest.stem + '_thumb.jpg')
            cv2.imwrite(str(thumb), frame)
        frame_count += 1
    cap.release()
    writer.release()
    print('Converted', src.name, '->', dest.name)
    return True

def main():
    in_files = [p for p in IN_DIR.iterdir() if p.suffix.lower() in ('.avi', '.mp4', '.mov')]
    if not in_files:
        print('No annotated outputs found in', IN_DIR)
        return
    for f in in_files:
        out_name = f.stem + '.mp4'
        dest = VID_DIR / out_name
        if f.suffix.lower() == '.mp4':
            shutil.copy(str(f), str(dest))
            print('Copied', f.name, '->', dest.name)
            # extract first frame
            cap = cv2.VideoCapture(str(dest))
            ret, frame = cap.read()
            if ret:
                thumb = IMG_DIR / (dest.stem + '_thumb.jpg')
                cv2.imwrite(str(thumb), frame)
            cap.release()
        else:
            convert_avi_to_mp4(f, dest)

    # write a videos.json in videos/ listing the new mp4s
    files = [p.name for p in VID_DIR.iterdir() if p.suffix.lower() == '.mp4']
    import json
    with open(VID_DIR / 'videos.json', 'w', encoding='utf-8') as fh:
        json.dump(files, fh, indent=2)
    print('Wrote videos/videos.json with', len(files), 'entries')

if __name__ == '__main__':
    main()
