#!/usr/bin/env python3
import argparse, json
from PIL import Image
p=argparse.ArgumentParser(); p.add_argument('image'); p.add_argument('--width',type=int); p.add_argument('--height',type=int); p.add_argument('--mode',default='RGB')
a=p.parse_args(); im=Image.open(a.image); issues=[]
if a.width and im.width!=a.width: issues.append({'code':'WIDTH','actual':im.width,'expected':a.width})
if a.height and im.height!=a.height: issues.append({'code':'HEIGHT','actual':im.height,'expected':a.height})
print(json.dumps({'pass':not issues,'width':im.width,'height':im.height,'mode':im.mode,'issues':issues},indent=2))
