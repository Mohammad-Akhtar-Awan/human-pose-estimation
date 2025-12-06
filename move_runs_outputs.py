from pathlib import Path
import shutil
base = Path('runs/pose')
out = Path('outputs_ultralytics')
out.mkdir(exist_ok=True)
if not base.exists():
    print('No runs/pose found')
else:
    for d in sorted(base.iterdir()):
        if d.is_dir():
            for f in d.iterdir():
                if f.suffix.lower() in ('.mp4', '.avi', '.mov'):
                    dest = out / f'annotated_{f.name}'
                    try:
                        shutil.move(str(f), str(dest))
                        print('Moved', f.name, '->', dest)
                    except Exception as e:
                        print('Failed move', f.name, e)
                elif f.suffix.lower() in ('.jpg', '.png'):
                    dest = out / f.name
                    shutil.move(str(f), str(dest))
                    print('Moved', f.name, '->', dest)
print('Done')
