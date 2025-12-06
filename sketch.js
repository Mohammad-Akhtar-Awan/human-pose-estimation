let posenet;
let singlePose, skeleton;
let face_img;
let vid;
let sourceSelect;
let currentSource = null; // only play local videos

function setup() {
    createCanvas(630,450,0,0);
    background(100);
    // vid = createVideo('videos/running.mp4');
    // vid.loop();
    // vid.hide();

    face_img = loadImage("images/batman.png");

    // source selector element (populated from videos/videos.json)
    sourceSelect = document.getElementById('sourceSelect');
    if (sourceSelect) {
        fetch('videos/videos.json')
            .then(res => res.json())
            .then(list => {
                list.forEach(fn => {
                    const opt = document.createElement('option');
                    opt.value = fn;
                    opt.innerText = fn;
                    sourceSelect.appendChild(opt);
                });
            }).catch(err => {
                console.log('No videos.json found or failed to load videos list', err);
            });

        sourceSelect.addEventListener('change', (e) => {
            const v = e.target.value;
            if (v) switchSource(v);
        });
    }

}


function posesReceived(poses) {
    console.log(poses);
    if (poses.length > 0) {
        singlePose = poses[0].pose;
        skeleton = poses[0].skeleton;
    }
}

function modelLoaded(){
    console.log("Model has loaded");
}
  
function draw() {
    // only play selected video
    if (vid && vid.elt && vid.elt.readyState >= 2) {
        image(vid, 0, 0, 630, 450);
    } else {
        // clear when no video
        background(40);
    }
    fill(0,255,0);
    if (singlePose) {
    for (let i=0; i<singlePose.keypoints.length; i++) {

        ellipse(singlePose.keypoints[i].position.x, singlePose.keypoints[i].position.y, 20, 20);
    }
    stroke(255,255,0);
    strokeWeight(4);
    for (let j=0; j<skeleton.length; j++) {
        
        line(skeleton[j][0].position.x, skeleton[j][0].position.y, skeleton[j][1].position.x, skeleton[j][1].position.y);
    }
    if (singlePose.pose) {
        image(face_img, singlePose.pose.x, singlePose.pose.y, 50, 50);
    }
    }
    
    
}

function switchSource(value) {
    // stop previous video if any
    if (vid) {
        try { vid.stop(); } catch(e){}
        vid.hide();
        vid = null;
    }

    // value is a path relative to server, e.g. videos/foo.mp4
    currentSource = 'video';
    vid = createVideo(['videos/' + value], () => {
        vid.loop();
        vid.volume(0);
        vid.hide();
    });
    // tell posenet to listen to the video element
    posenet = ml5.poseNet(vid, modelLoaded);
    posenet.on('pose', posesReceived);
}