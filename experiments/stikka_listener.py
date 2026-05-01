import paho.mqtt.client as mqtt
import json
import base64
import os
import time
from PIL import Image
from io import BytesIO
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert

# --- CONFIGURATION ---
# Ganti dengan Pi Printer ID yang ada di web (misal: stikka-pi-abcde)
PI_PRINTER_ID = "GANTI_DENGAN_ID_DARI_WEB" 
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
TOPIC = f"stikka/print/{PI_PRINTER_ID}"

# Pengaturan Printer (Bisa disesuaikan lewat payload dari web nanti)
PRINTER_MODEL = "QL-550" # Contoh: QL-550, QL-700, QL-800
PRINTER_USB = "usb://0x04f9:0x2015" # Cek dengan command 'lsusb' jika tidak jalan

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[*] Terhubung ke Broker! Menunggu perintah cetak di topik: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"[!] Gagal terhubung, kode: {rc}")

def on_message(client, userdata, msg):
    try:
        print(f"\n[+] Menerima perintah cetak baru!")
        data = json.loads(msg.payload.decode())
        job_name = data.get('jobName', 'Job')
        image_b64 = data.get('image', '').split(',')[1] # Ambil base64 setelah 'data:image/png;base64,'
        
        # Decode image
        img_data = base64.b64decode(image_b64)
        img = Image.open(BytesIO(img_data))
        
        # Simpan sementara (opsional)
        temp_filename = "last_print.png"
        img.save(temp_filename)
        print(f"    - Nama Job: {job_name}")
        print(f"    - Ukuran: {img.size[0]}x{img.size[1]} px")

        # Proses Cetak dengan brother_ql
        # Note: Kita asumsikan model default QL-550 dan tape 62mm
        model = data.get('profile', 'QL-550').upper().replace('QL', 'QL-')
        if model == 'QL-550': model = 'QL-550' # Fix format
        
        qlr = BrotherQLRaster(model)
        qlr.exception_on_warning = True
        
        # Konversi gambar ke format raster printer
        # label size bisa disesuaikan (misal 62 untuk tape 62mm)
        instructions = convert(
            qlr=qlr, 
            images=[img], 
            label='62', # Tape width 62mm
            rotate='0', 
            threshold=70, 
            dither=False, 
            compress=False, 
            red=False, 
            cut=True if data.get('cut') == 'full' else False
        )
        
        # Kirim ke printer USB
        # Jika Anda tidak tahu ID USB printer, biarkan library mencarinya otomatis
        # atau gunakan 'brother_ql discover' di terminal Pi
        send(instructions=instructions, printer_identifier=PRINTER_USB, backend_identifier='pyusb')
        
        print(f"[✓] Berhasil mencetak: {job_name}")
        
    except Exception as e:
        print(f"[!] ERROR saat mencetak: {e}")

# Inisialisasi MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"[*] Menghubungkan ke broker {MQTT_BROKER}...")
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[!] Program dihentikan.")
except Exception as e:
    print(f"[!] Gagal menjalankan script: {e}")
