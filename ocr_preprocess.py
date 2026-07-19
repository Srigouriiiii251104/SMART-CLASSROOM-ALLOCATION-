from PIL import Image, ImageOps
import easyocr

img_path = r'E:/pbl/WhatsApp Image 2026-07-04 at 7.49.46 PM.jpeg'
reader = easyocr.Reader(['en'], gpu=False)
for angle in [0, -90, 90, 180]:
    img = Image.open(img_path)
    if angle != 0:
        img = img.rotate(angle, expand=True)
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray)
    out_name = rf'E:/pbl/ocr_test_{angle}.png'
    gray.save(out_name)
    print('ANGLE', angle, 'saved', out_name)
    text = reader.readtext(out_name, detail=0, paragraph=True)
    print('---', angle, '---')
    print('\n'.join(text))
    print('')
