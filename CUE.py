import os
import sys
import subprocess

metadata = {b"TITLE": [], b"PERFORMER": [], b"INDEX": [], b"REM COMPOSER": []}

def timedif(i1, i2):
    i1, i2 = i1.split(":"), i2.split(":")
    a = (int(i1[0]) * 60) + int(i1[1])
    b = (int(i2[0]) * 60) + int(i2[1])
    return b - a


def cuedata(pth):
    with open(pth, "+r", encoding="utf-8") as ff:
        f = ff.read()
        k = f.encode("utf-8")
    ff = k.split(b"TRACK")
    ff.pop(0)
    for i in ff:
        for spi in i.split(b"\n"):
            for ky in metadata:
                if ky in spi:
                    if ky == b"INDEX":
                        spi = spi.split(ky)[1].strip().split(b" ")[1]
                    else:
                        spi = spi.split(ky)[1].strip().strip(b'""')
                    metadata[ky].append(spi)
                    break
    return metadata


def chaff(time):
    min, sec = time.split(":")
    min = int(min)
    sec = int(sec)
    if min > 59:
        hr = min // 60
        min %= 60
        if hr == 0:
            return "%02d:%02d" % (min, sec)
        elif hr < 10:
            return "0%0d:%02d:%02d" % (hr, min, sec)
        else:
            return "%d:%02d:%02d" % (hr, min, sec)
    return time


def validtitle(name):
    for inva in ["/", "\\", "?", "%", "*", ":", "|", "”", "<", ">"]:
        if inva in name:
            name = name.replace(inva, "")
    return name


def main(arg=sys.argv[1:]):
    if not arg or not os.path.isfile(arg[0]):
        print(f"The path '{arg[0]}' is not valid." if arg else "No input file specified.")
        exit()

    if os.path.splitext(arg[0])[1].lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
        print(f"The extension of the file '{arg[0]}' is unrecognised.")
        exit()
        
    if arg and os.path.isfile(arg[0]) and os.path.splitext(arg[0])[1].lower() in ['.png','.jpg','.jpeg','.webp']:
        asmodeus=arg[0]

    repm = ""
    while not os.path.exists(repm):
        repm = input("Location of CUE:")
        if repm.lower() == "break":
            exit()
        if not os.path.exists(repm):
            print('Location not valid. Try again or use "break" to exit')

    dspth = ""
    while True:
        dspth = input("\nExtract Location:")
        if dspth == "" or dspth.lower() == "break":
            exit()
        if not os.path.exists(dspth):
            print("Location not valid. Press Enter or enter a valid location")
        else:
            break

    reps = os.listdir(repm)
    treatgm = False

    for rep in reps:
        if rep.lower().endswith(".cue"):
            treatgm = True
            rep = os.path.join(repm, rep)
            chk = 0

            for i in ["flac", "m4a", "mp3", "aac", "wav", "ogg", "tta"]:
                loc = rep[:-3] + i
                print(loc)
                if os.path.exists(loc):
                    chk = 1
                    break

            if not chk:
                print("\nAudio file not found.")
                continue

            datacu = cuedata(rep)
            mfile = loc
            ext = loc[loc.rindex(".") :]

            if not arg:
                cimg = [
                    "ffmpeg",
                    "-hide_banner",
                    "-y",
                    "-i",
                    mfile,
                    "-an",
                    "-vcodec",
                    "copy",
                    "cover.png",
                ]
                aimg = subprocess.run(
                    cimg, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                asmodeus = "cover.png"

            a, b, wolfe = 0, 0, 0
            print("\n", "—" * 55)

            for i in datacu[b"TITLE"]:
                i = i.decode("utf-8")
                ior = validtitle(i)
                otfl = f'{ior+"_tmp"+ext}'
                otfl_fn = f"{ior+ext}"
                
                if dspth:
                    otfl = os.path.join(dspth, otfl)
                    otfl_fn = os.path.join(dspth, otfl_fn)

                tit = f"title={i}"
                artt = "artist=" + datacu[b"PERFORMER"][a].decode("utf-8")
                atime = datacu[b"INDEX"][b : b + 2]

                if len(atime) == 1:
                    wolfe = 1
                    stime = atime[0].decode("utf-8")
                else:
                    stime, etime = (
                        atime[0].decode("utf-8").strip(),
                        atime[1].decode("utf-8").strip(),
                    )
                    diff = str(timedif(stime, etime))

                stime = stime.rsplit(":", 1)[0]
                stime = chaff(stime)
                a += 1
                b += 2
                trno = f"track={a}"
                print(f"TRACK {a}: {i}")

                if wolfe:
                    if ext != ".flac":
                        cmd = [
                            "ffmpeg",
                            "-hide_banner",
                            "-ss",
                            stime,
                            "-y",
                            "-i",
                            mfile,
                            "-avoid_negative_ts",
                            "make_zero",
                            "-c",
                            "copy",
                            "-metadata",
                            tit,
                            "-metadata",
                            artt,
                            "-metadata",
                            trno,
                            otfl,
                        ]
                    else:
                        cmd = [
                            "ffmpeg",
                            "-hide_banner",
                            "-ss",
                            stime,
                            "-y",
                            "-i",
                            mfile,
                            "-avoid_negative_ts",
                            "make_zero",
                            "-map",
                            "0",
                            "-metadata",
                            tit,
                            "-metadata",
                            artt,
                            "-metadata",
                            trno,
                            otfl,
                        ]
                else:  # wolfe = 0
                    if ext != ".flac":
                        cmd = [
                            "ffmpeg",
                            "-hide_banner",
                            "-ss",
                            stime,
                            "-y",
                            "-i",
                            mfile,
                            "-t",
                            diff,
                            "-avoid_negative_ts",
                            "make_zero",
                            "-c",
                            "copy",
                            "-metadata",
                            tit,
                            "-metadata",
                            artt,
                            "-metadata",
                            trno,
                            otfl,
                        ]
                    else:
                        cmd = [
                            "ffmpeg",
                            "-hide_banner",
                            "-ss",
                            stime,
                            "-y",
                            "-i",
                            mfile,
                            "-t",
                            diff,
                            "-map",
                            "0",
                            "-metadata",
                            tit,
                            "-metadata",
                            artt,
                            "-metadata",
                            trno,
                            otfl,
                        ]
                
                aa = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )

                cimgad = [
                    "ffmpeg",
                    "-hide_banner",
                    "-y",
                    "-i",
                    otfl,
                    "-i",
                    asmodeus,
                    "-map",
                    "0:a",
                    "-map",
                    "1",
                    "-codec",
                    "copy",
                    "-metadata:s:v",
                    'title="Album cover"',
                    "-metadata:s:v",
                    'comment="Cover (front)"',
                    "-disposition:v",
                    "attached_pic",
                    otfl_fn,
                ]
                
                aimgad = subprocess.run(
                    cimgad, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                )
                
                os.remove(otfl)

            if not arg:
                os.remove(asmodeus)

    if not treatgm:
        print("\nNo CUE file found.")


if __name__ == "__main__":
    main()
