import math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
OUT='/home/user/generative-art-node/rova-memes'
BG=(244,244,245); W=720
src=Image.open('rova_source.png').convert('RGB')
# cutout: pixels differing from bg -> alpha; crop to box (exclude soft shadow by threshold)
diff=ImageChops.difference(src,Image.new('RGB',src.size,BG)).convert('L')
mask=diff.point(lambda v:255 if v>14 else 0).filter(ImageFilter.MedianFilter(5))
# fill holes via flood from outside
m=mask.copy(); ImageDraw.floodfill(m,(0,0),128)
mask=m.point(lambda v:0 if v==128 else 255).filter(ImageFilter.GaussianBlur(0.8))
prod=src.copy(); prod.putalpha(mask); prod=prod.crop(mask.getbbox())
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(s): return ImageFont.truetype(FONT,s)
def shadow(w,alpha):
    sh=Image.new('L',(W,W),0); d=ImageDraw.Draw(sh)
    cx,cy=W//2,560
    d.ellipse([cx-w,cy-w*0.18,cx+w,cy+w*0.18],fill=int(alpha))
    return sh.filter(ImageFilter.GaussianBlur(18))
def place(canvas,p,cx,bottom,sx=1,sy=1,rot=0):
    q=p.resize((max(1,int(p.width*sx)),max(1,int(p.height*sy))),Image.LANCZOS)
    if rot: q=q.rotate(rot,resample=Image.BICUBIC,expand=True)
    canvas.paste(q,(int(cx-q.width/2),int(bottom-q.height)),q)
def caption(img,top,bottom=None,dark=True):
    d=ImageDraw.Draw(img); col=(25,25,30) if dark else (255,255,255)
    for txt,y in ((top,60),(bottom,650)):
        if not txt: continue
        s=46
        while d.textlength(txt,font=font(s))>W-60: s-=2
        d.text((W/2,y),txt,font=font(s),fill=col,anchor='mm')
def save(frames,name,dur=40):
    frames[0].save(f'{OUT}/{name}.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0,optimize=True)
    print(name,len(frames))
base_bottom=540
# 1) Drop & bounce with squash
fr=[]
N=50
for i in range(N):
    t=i/N
    if t<0.35: y=-300+ (base_bottom+300)*(t/0.35)**2; sx=sy=1
    else:
        u=(t-0.35)/0.65; off=abs(math.sin(u*math.pi*3))*120*math.exp(-4*u); y=base_bottom-off
        sq=0.12*math.exp(-5*u)*max(0,math.cos(u*math.pi*6)); sx,sy=1+sq,1-sq
    c=Image.new('RGB',(W,W),BG)
    a=max(0,min(1,(y+300)/(base_bottom+300)))
    c.paste((205,205,210),mask=shadow(220*(0.5+0.5*a),140*a))
    place(c,prod,W/2,y,sx,sy); fr.append(c)
fr+= [fr[-1]]*15
save(fr,'01_drop_bounce')
# 2) Hover/float loop
fr=[]
for i in range(40):
    t=i/40*2*math.pi; off=18*math.sin(t)
    c=Image.new('RGB',(W,W),BG); c.paste((205,205,210),mask=shadow(220-off*1.5,130-off*2))
    place(c,prod,W/2,base_bottom-40-off,rot=1.5*math.sin(t+0.6)); fr.append(c)
save(fr,'02_float_loop',50)
# 3) Meme: excited shake + caption
fr=[]
for i in range(30):
    c=Image.new('RGB',(W,W),BG); c.paste((205,205,210),mask=shadow(220,130))
    j=8*math.sin(i*2.1) if (i//10)%3!=2 else 0
    place(c,prod,W/2+j,base_bottom,rot=2*math.sin(i*1.7) if j else 0)
    caption(c,'Montag, 8:00 Uhr.','Rova hat die Aufgaben schon verteilt.')
    fr.append(c)
save(fr,'03_meme_montag',60)
# 4) Meme: pop-in zoom + punchline
fr=[]
for i in range(45):
    t=min(1,i/14); s=0.2+0.8*(1+1.7*(t-1)**3+0.7*(t-1)**2) if i<14 else 1
    c=Image.new('RGB',(W,W),BG); c.paste((205,205,210),mask=shadow(220*s,130*s))
    place(c,prod,W/2,base_bottom,s,s)
    caption(c,'Chef: „Wer kümmert sich drum?“',None)
    if i>=22: caption(c,None,'Rova: „Schon erledigt.“')
    fr.append(c)
save(fr,'04_meme_erledigt',60)
