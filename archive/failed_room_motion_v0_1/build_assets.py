"""Build a proof-of-concept interactive scene from the approved Lalin room image.

Input raster is NOT equivalent to production layered art. Polygon-mask cutouts and
OpenCV inpainting here demonstrate the scene graph; rebuild clean plates and
riggable assets for final animation.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import cv2, json, shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'source_room.png'
IMG = Image.open(SOURCE).convert('RGB')
W,H = IMG.size
assert (W,H)==(1672,941)
BASE = np.array(IMG)

# Manually traced approximate contours in the approved image's pixel coordinates.
# These are rough prototype masks, NOT final animation mattes.
PROPS = [
  dict(id='phone', name='Telefon', contour=[(1510,428),(1554,431),(1556,443),(1526,520),(1516,534),(1473,528),(1470,522),(1495,450)],
       anchor=[.52,.97], amp=3, foley='phone_vibrate'),
  dict(id='cat', name='Uyuyan kedi', contour=[(1090,827),(1104,807),(1123,798),(1137,755),(1154,784),(1172,776),(1188,765),(1219,751),(1252,750),(1279,755),(1300,762),(1322,765),(1344,779),(1361,794),(1375,808),(1379,826),(1368,849),(1343,854),(1304,860),(1257,859),(1228,871),(1194,867),(1165,855),(1132,859),(1105,847)],
       anchor=[.50,.88], amp=1.5, foley='cat_purr'),
  dict(id='flowers', name='Çiçekli vazo', contour=[(1133,340),(1119,334),(1100,318),(1111,304),(1125,303),(1135,312),(1139,299),(1149,290),(1163,296),(1176,285),(1191,294),(1197,306),(1215,297),(1224,307),(1223,320),(1248,325),(1245,337),(1220,346),(1229,359),(1215,367),(1210,381),(1209,463),(1199,479),(1158,479),(1147,468),(1147,379),(1122,372),(1115,357)],
       anchor=[.5,.95], amp=1.5, foley='glass_tink'),
]

outprops = []
mask_total = np.zeros((H,W),np.uint8)
for p in PROPS:
    poly = p['contour']
    pm = Image.new('L',(W,H),0)
    ImageDraw.Draw(pm).polygon(poly,fill=255)
    alpha = np.array(pm)
    # Grabcut matting: keep reliable inner core, probable on contours, definitely outside.
    # Iterative graph-cut may spoil wispy flowers: for flowers use softly feathered polygon.
    if p['id']=='cat':
        work = np.full((H,W),cv2.GC_BGD,np.uint8)
        dil = cv2.dilate(alpha,np.ones((11,11),np.uint8))
        ero = cv2.erode(alpha,np.ones((9,9),np.uint8))
        work[dil>0]=cv2.GC_PR_BGD
        work[alpha>0]=cv2.GC_PR_FGD
        # Fuzzy feline vs pink bed: core of pale fur is a strong foreground seed.
        sel = (ero>0) & (BASE[:,:,0]>182) & (BASE[:,:,1]>160) & (BASE[:,:,2]>153)
        work[sel]=cv2.GC_FGD
        if np.any(sel):
            try:
                bgm=np.zeros((1,65),np.float64); fgm=np.zeros((1,65),np.float64)
                cv2.grabCut(cv2.cvtColor(BASE,cv2.COLOR_RGB2BGR),work,None,bgm,fgm,4,cv2.GC_INIT_WITH_MASK)
                fg=np.where((work==2)|(work==0),0,255).astype('uint8')
                # Keep segmentation within traced contour, soft edges.
                alpha = cv2.bitwise_and(alpha,fg)
                if np.count_nonzero(alpha)<4000: alpha = np.array(pm)
            except cv2.error: pass
    # Keep raw cutouts a bit inside approximate outline to reduce visible halos.
    alpha = cv2.GaussianBlur(alpha,(5,5),1.2)
    ys,xs=np.nonzero(alpha>2)
    if not len(xs): raise ValueError('Empty mask '+p['id'])
    x0,x1=max(xs.min()-3,0),min(xs.max()+4,W)
    y0,y1=max(ys.min()-3,0),min(ys.max()+4,H)
    rgba=np.zeros((y1-y0,x1-x0,4),np.uint8)
    rgba[:,:,:3]=BASE[y0:y1,x0:x1]
    rgba[:,:,3]=alpha[y0:y1,x0:x1]
    f=ROOT/'assets/props'/f"{p['id']}.png"
    Image.fromarray(rgba,'RGBA').save(f,optimize=True)
    # slightly dilated removal areas to reduce ghosting
    mask_total=np.maximum(mask_total,cv2.dilate((alpha>30).astype('uint8')*255,np.ones((5,5),np.uint8)))
    outprops.append(dict(id=p['id'],label=p['name'],image=f'assets/props/{p["id"]}.png',x=int(x0),y=int(y0),width=int(x1-x0),height=int(y1-y0),anchor=p['anchor'],foley=p['foley']))

# OpenCV synthesized background is deliberately a TEMPORARY clean plate.
# It will be covered by the props at rest. Moving the props far may show defects.
clean = cv2.inpaint(cv2.cvtColor(BASE,cv2.COLOR_RGB2BGR),mask_total,5,cv2.INPAINT_TELEA)
Image.fromarray(cv2.cvtColor(clean,cv2.COLOR_BGR2RGB)).save(ROOT/'assets/clean_plate.jpg',quality=93,subsampling=0)

scene = {
  'name':'Lalin — Giyinme Odası', 'version':'0.1.0-prototype',
  'canvas':{'width':W,'height':H,'fps':30},
  'reference':'source_room.png','cleanPlate':'assets/clean_plate.jpg',
  'space':'fixed 2D background, camera-relative pixels',
  'props':outprops,
  'lockedVisuals':['wardrobe layout','main mirror','window and Bosphorus view','pink/burgundy/gold palette','neon sign','furniture locations'],
  'futureRiggedAssets':['curtains','vanity drawers','lipstick and its cap','handbag','vanity mirror and reflection','cosmetics','clothes on hangers','cat body/face'],
  'foleyEvents':[
   {'name':'heel_step_marble','event':'foot_contact','sync':'same-frame','placeholder':True},
   {'name':'bag_placed','event':'bag_surface_contact','sync':'same-frame','placeholder':True},
   {'name':'phone_vibrate','event':'phone_vibration_onset','sync':'same-frame','placeholder':True},
   {'name':'glass_tink','event':'glass_collision','sync':'same-frame','placeholder':True},
  ],
  'constraints':['At rest reconstruct approved composition','No random object teleportation','A prop must disappear from the table while held','No double-image shadows when an object moves','Occluded pixels must be independently redrawn for final', 'Character mirror reflection must follow movement when visible'],
  'notes':'Prototype masks and inpainted clean plate are approximate. Not a production-ready rig or true reflection system.'
}
(ROOT/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
print('Generated',outprops)
