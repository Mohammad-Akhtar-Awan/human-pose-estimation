import os
import cv2
import json
from pathlib import Path
import mediapipe as mp

BASE_DIR = Path(__file__).parent
VIDEOS_DIR = BASE_DIR / 'videos'
OUTPUT_DIR = BASE_DIR / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

VIDEO_EXTS = ['.mp4', '.mov', '.avi', '.mkv']

def list_videos():
    files = [f.name for f in VIDEOS_DIR.iterdir() if f.suffix.lower() in VIDEO_EXTS]
    return files

def annotate_video(filename):
    in_path = VIDEOS_DIR / filename
    cap = cv2.VideoCapture(str(in_path))
    if not cap.isOpened():
        print(f'Failed to open {in_path}')
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out_path = OUTPUT_DIR / f'annotated_{filename}'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    snapshot_saved = False

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            annotated = frame.copy()
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    annotated,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255,255,0), thickness=2)
                )

            writer.write(annotated)

            # save first annotated frame as snapshot
            if not snapshot_saved:
                snap_path = OUTPUT_DIR / f'{Path(filename).stem}_snapshot.jpg'
                cv2.imwrite(str(snap_path), annotated)
                snapshot_saved = True

            frame_idx += 1

    cap.release()
    writer.release()
    print(f'Wrote annotated video to {out_path} and snapshot')


def main():
    videos = list_videos()
    if not videos:
        print('No video files found in videos/ folder. Place .mp4/.mov/.avi files there.')
        return

    for v in videos:
        print('Processing', v)
        annotate_video(v)

    # write videos.json for browser UI
    videos_json_path = VIDEOS_DIR / 'videos.json'
    with open(videos_json_path, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2)
    print('Wrote', videos_json_path)


if __name__ == '__main__':
    main()
