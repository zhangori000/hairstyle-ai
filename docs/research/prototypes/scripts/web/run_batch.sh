#!/bin/bash
# Sequential benchmark variants (never concurrent: 4 CPUs, timings must not contend).
cd "$(dirname "$0")"
run() { echo "=== $1 ($(date +%T)) ==="; node drive.cjs --name "$1" --params "$2" --y4m "$3" --gpu "$4" $5 2>&1 | grep -v "inference_feedback_manager\|XNNPACK\|gl_context\|Graph finished\|Graph successfully\|FaceBlendshapesGraph" | cut -c1-900 | grep "loop\|worker\|init\|image\|camera\|gl_overlay\|DONE\|FAILED\|error\|Error\|requestfailed\|pageerror\|phase\]" ; }
run cpu_remote      "delegate=CPU&models=remote&frames=60" cam/face_640x480.y4m  none --proxy
run gpu_noflags     "delegate=GPU&models=local&frames=30"  cam/face_640x480.y4m  none
run gpu_swiftshader "delegate=GPU&models=local&frames=30"  cam/face_640x480.y4m  swiftshader
run cpu_720p        "delegate=CPU&models=local&frames=60&w=1280&h=720" cam/face_1280x720.y4m none
run cpu_240p        "delegate=CPU&models=local&frames=60&w=320&h=240"  cam/face_320x240.y4m  none
echo "=== BATCH DONE ($(date +%T)) ==="
