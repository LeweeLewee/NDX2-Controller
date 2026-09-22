"""Create a reproducible vendor-based fixture build without replacing a checkout."""
import argparse
import hashlib
from pathlib import Path
import shutil
import re
import zipfile

SHA256 = '57186c266f5ed5d9cd22b80b3d3d1d19d54dec2449d7ec220c8b3abc60ee0092'
PREFIX = 'ESP32-S3-Touch-LCD-4.3B-BOX-Demo/ESP-IDF/08_lvgl_Porting/'
ROOT = Path(__file__).resolve().parents[1]

def sync_sources(output):
    """Refresh only our generated overlay, never vendor drivers or configuration."""
    output=Path(output).resolve()
    marker=output/'M2_BUILD.txt'
    if not output.is_relative_to((ROOT/'local').resolve()) or not marker.is_file() or SHA256 not in marker.read_text():
        raise ValueError('Expected an owned checksum-pinned generated project')
    for directory in ('shared','esp32'):
        for path in (ROOT/'firmware'/directory).glob('*.[ch]'):
            target=output/'main'/path.name
            if not target.exists() or target.read_bytes()!=path.read_bytes(): shutil.copyfile(path,target)
    (output/'main/CMakeLists.txt').write_text(
        'idf_component_register(SRCS "waveshare_rgb_lcd_port.c" "main.c" "lvgl_port.c" "controller.c" "ui.c" "fixture.c" "bridge_protocol.c" "bridge_transport.c" "preferences.c" "preferences_nvs.c" INCLUDE_DIRS ".")\n'
        'idf_component_get_property(json_lib json COMPONENT_LIB)\n'
        'target_compile_definitions(${json_lib} PRIVATE CJSON_NESTING_LIMIT=16)\n')
    for name in ('sdkconfig.defaults','sdkconfig'):
        path=output/name
        if path.exists():
            config=path.read_text()
            for size in (16, 20, 24, 32):
                pattern=r'^(?:# )?CONFIG_LV_FONT_MONTSERRAT_'+str(size)+r'(?:=.*| is not set)$'
                setting='CONFIG_LV_FONT_MONTSERRAT_'+str(size)+'=y'
                config=re.sub(pattern,setting,config,flags=re.M) if re.search(pattern,config,re.M) else config+'\n'+setting+'\n'
            config=re.sub(r'^(?:# )?CONFIG_LV_(?:USE_DEMO_(?:WIDGETS|BENCHMARK|STRESS|MUSIC)|DEMO_MUSIC_AUTO_PLAY)(?:=.*| is not set)\n?', '', config, flags=re.M)
            config=config.rstrip()+'\n\n'+''.join('# CONFIG_LV_'+flag+' is not set\n' for flag in
                ('USE_DEMO_WIDGETS','USE_DEMO_BENCHMARK','USE_DEMO_STRESS','USE_DEMO_MUSIC','DEMO_MUSIC_AUTO_PLAY'))
            if config!=path.read_text(): path.write_text(config)


def prepare(archive, output, touch_reviewed=False):
    raw = Path(archive).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError('Vendor archive changed; review before updating the pinned checksum')
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'local').resolve()):
        raise ValueError('Generated vendor project must remain under ignored local/')
    output.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if not name.startswith(PREFIX) or name.endswith('/'): continue
            target = (output / name[len(PREFIX):]).resolve()
            if not target.is_relative_to(output): raise ValueError('Unsafe archive path')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))
    for path in (ROOT/'firmware/shared').iterdir():
        shutil.copyfile(path, output/'main'/path.name)
    for path in (ROOT/'firmware/esp32').glob('*.[ch]'):
        shutil.copyfile(path, output/'main'/path.name)
    cmake = output/'main/CMakeLists.txt'
    cmake.write_text('idf_component_register(SRCS "waveshare_rgb_lcd_port.c" "main.c" "lvgl_port.c" "controller.c" "ui.c" "fixture.c" "bridge_protocol.c" "bridge_transport.c" "preferences.c" "preferences_nvs.c" INCLUDE_DIRS ".")\n')
    # Components are vendored inside the checksum-pinned archive. Disable floating registry resolution.
    (output/'main/idf_component.yml').write_text('dependencies:\n  idf: "==5.2.0"\n')
    config = output/'sdkconfig.defaults'
    with config.open('a') as f:
        f.write('\nCONFIG_LV_USE_DEMO_WIDGETS=n\nCONFIG_LV_USE_DEMO_MUSIC=n\nCONFIG_LV_DEMO_MUSIC_AUTO_PLAY=n\n')
    if touch_reviewed:
        port = output/'main/lvgl_port.h'
        text=port.read_text()
        old='#define CONFIG_EXAMPLE_LCD_TOUCH_CONTROLLER_GT911 0'
        if old not in text: raise ValueError('Touch configuration changed')
        port.write_text(text.replace(old, '#define CONFIG_EXAMPLE_LCD_TOUCH_CONTROLLER_GT911 1'))
    port=output/'main/lvgl_port.c'
    text=port.read_text()
    old='if (touchpad_pressed && touchpad_cnt > 0) {'
    if text.count(old)!=1: raise ValueError('Touch callback changed')
    text='#include "ui.h"\n'+text.replace(old,
        'if (controller_ui_touch(touchpad_pressed && touchpad_cnt > 0)) {')
    port.write_text(text)
    (output/'M2_BUILD.txt').write_text('SILENT FIXTURE\nESP-IDF v5.2.0\nLVGL 8.4.0\nArchive SHA256 '+SHA256+
        '\nTouch enabled after explicit revision review: '+str(touch_reviewed)+
        '\nNo deep/light sleep or microphone pins configured.\n')
    print('Prepared',output)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--archive',default='local/m2/vendor.zip')
    parser.add_argument('--out',default='local/m2/esp32-fixture')
    parser.add_argument('--touch-reviewed',action='store_true',help='Only after actual board revision/driver review')
    args=parser.parse_args(); prepare(args.archive,args.out,args.touch_reviewed)
