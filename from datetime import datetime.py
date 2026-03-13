from datetime import datetime
import pytz

# Türkiye saat dilimi
turkey_tz = pytz.timezone('Europe/Istanbul')
# Gürcistan saat dilimi
georgia_tz = pytz.timezone('Asia/Tbilisi')

now_utc = datetime.now(pytz.utc)
turkey_time = now_utc.astimezone(turkey_tz)
georgia_time = now_utc.astimezone(georgia_tz)

# Saat farkını hesapla
hour_difference = (georgia_time - turkey_time).total_seconds() / 3600

# Kırım Tatarı ruh hali için uygun bir selamlama
greeting = "Selâm aleküm, dostlar! Bugün kendimi Kırım Tatarı gibi hissettim; umutlu, güçlü ve dayanışmaya açık!"

print(greeting)
print(f"Şu anda Türkiye saati: {turkey_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Şu anda Gürcistan saati: {georgia_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Gürcistan ile Türkiye arasındaki saat farkı: {int(hour_difference)} saat")