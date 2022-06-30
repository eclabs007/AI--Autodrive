pico2wave -w=/tmp/test.wav "$1"
aplay /tmp/test.wav  -D plughw:2,0

rm /tmp/test.wav  -f

