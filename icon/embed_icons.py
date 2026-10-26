import base64
icons = {
    '192': 'gpay-apk/res/mipmap-xxxhdpi/ic_launcher.png',
    '96':  'gpay-apk/res/mipmap-xxhdpi/ic_launcher.png',
    '48':  'gpay-apk/res/mipmap-xhdpi/ic_launcher.png',
}
imgs = []
for w, p in icons.items():
    b64 = base64.b64encode(open(p, 'rb').read()).decode()
    imgs.append(f'<img src="data:image/png;base64,{b64}" width="{w}" style="image-rendering:pixelated;background:#fff;border-radius:{int(int(w)*0.13)}px;">')
html = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Icon check</title></head>\n<body style="display:flex; gap:24px; align-items:center; justify-content:center; height:100vh; background:#888;">\n' + '\n'.join(imgs) + '\n</body></html>'
open('gpay-apk/icon/preview_icon.html', 'w').write(html)
print('wrote preview_icon.html with', len(imgs), 'embedded icons')
