"""Render the layer-motion concept into a SILENT 6 s mp4 (no foley is faked)."""
from pathlib import Path
import numpy as np, cv2, math, subprocess
ROOT=Path(__file__).resolve().parent
BASE=cv2.imread(str(ROOT/'assets/clean_plate.jpg'),cv2.IMREAD_COLOR)
props={}
for p in ['flowers','phone','cat']:
    props[p]=cv2.imread(str(ROOT/'assets/props'/f'{p}.png'),cv2.IMREAD_UNCHANGED)
orig={'flowers':(1095,280),'phone':(1465,423),'cat':(1087,747)}
factor=960/1672
width=960;height=round(BASE.shape[0]*factor)
base=cv2.resize(BASE,(width,height),interpolation=cv2.INTER_AREA)
for k,a in props.items():
    size=(int(a.shape[1]*factor),int(a.shape[0]*factor))
    props[k]=cv2.resize(a,size,interpolation=cv2.INTER_AREA)
fourcc=cv2.VideoWriter_fourcc(*'mp4v')
tmp=ROOT/'uncompressed-preview.mp4'
out=cv2.VideoWriter(str(tmp),fourcc,30,(width,height))
assert out.isOpened()
for i in range(180):
    t=i/30
    canvas=base.copy()
    for id in ['flowers','phone','cat']:
        layer=props[id]
        h,w=layer.shape[:2]
        x,y=tuple(int(k*factor) for k in orig[id])
        if id=='flowers': angle=math.degrees(math.sin(t*1.22)*.012); sy=1; dx=0
        elif id=='cat': angle=0; sy=1+math.sin(t*2.3)*.007; dx=0
        else: angle=math.sin((t-2)*math.pi*30)*.343 if 2<=t<2.8 else 0; sy=1;dx=math.sin((t-2)*math.pi*30)*2.5*factor if 2<=t<2.8 else 0
        cx=w*.5;cy=h*.93
        M=cv2.getRotationMatrix2D((cx,cy),angle,1.0)
        M[1,1]*=sy
        M[0,2]+=dx
        warped=cv2.warpAffine(layer,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
        # composite crop with boundaries
        xx=max(x,0);yy=max(y,0);x2=min(x+w,width);y2=min(y+h,height)
        if xx>=x2 or yy>=y2:continue
        roi=canvas[yy:y2,xx:x2]
        fg=warped[yy-y:y2-y,xx-x:x2-x]
        alpha=(fg[:,:,3:4].astype(np.float32)/255.)
        roi[:]=(fg[:,:,:3]*alpha+roi*(1-alpha)).astype(np.uint8)
    out.write(canvas)
out.release()
result=ROOT/'animation-test.mp4'
proc=subprocess.run(['ffmpeg','-hide_banner','-y','-loglevel','error','-i',str(tmp),'-c:v','libx264','-crf','20','-preset','fast','-movflags','+faststart','-pix_fmt','yuv420p',str(result)],capture_output=True,text=True)
if proc.returncode: print(proc.stderr)
tmp.unlink(missing_ok=True)
print(result, result.stat().st_size if result.exists() else 'FAILED')
