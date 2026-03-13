import pandas as pd
import random
from datetime import datetime, timedelta

# Kategoriler
kategoriler = ['Sarap', 'Hostel', 'Kaos Ritüeli', 'Python Egitim', 'Hacapuri']

veri = []
baslangic_tarihi = datetime.now()
for i in range(15):
    tarih = (baslangic_tarihi + timedelta(days=i)).strftime('%Y-%m-%d')
    kategori = random.choice(kategoriler)
    harcama = round(random.uniform(10, 150), 2)  # 10 ila 150 GEL arası rastgele harcama
    veri.append({'Tarih': tarih, 'Kategori': kategori, 'Harcama_GEL': harcama})

df = pd.DataFrame(veri)
df.to_csv('kutaisi_kaos.csv', index=False)

# CSV'den oku
df2 = pd.read_csv('kutaisi_kaos.csv')

# Toplam harcama
toplam_harcama = df2['Harcama_GEL'].sum()
print(f"Toplam Harcama (GEL): {toplam_harcama:.2f}")

# Kategori bazlı harcama dağılımı
kat_bazli = df2.groupby('Kategori')['Harcama_GEL'].sum()
print("\nKategori Bazlı Harcama Dağılımı (GEL):")
print(kat_bazli)
import pandas as pd
import matplotlib.pyplot as plt

# CSV'den veri oku
df2 = pd.read_csv('kutaisi_kaos.csv')

# Kategori bazlı harcama
kat_bazli = df2.groupby('Kategori')['Harcama_GEL'].sum()

# Bar grafiği
plt.figure(figsize=(8,5))
kat_bazli.plot(kind='bar', color='skyblue')
plt.title('Kategori Bazlı Harcama Dağılımı (GEL)')
plt.xlabel('Kategori')
plt.ylabel('Toplam Harcama (GEL)')
plt.tight_layout()
plt.show()

# Pasta grafiği
plt.figure(figsize=(6,6))
kat_bazli.plot(kind='pie', autopct='%1.1f%%', startangle=90)
plt.title('Kategori Bazlı Harcama Dağılımı (Yüzde)')
plt.ylabel('')
plt.tight_layout()
plt.show()
import random
from datetime import datetime, timedelta

# Kategoriler
kategoriler = ['Sarap', 'Hostel', 'Kaos Ritüeli', 'Python Egitim', 'Hacapuri']

veri = []
baslangic_tarihi = datetime.now()
for i in range(15):
    tarih = (baslangic_tarihi + timedelta(days=i)).strftime('%Y-%m-%d')
    kategori = random.choice(kategoriler)
    harcama = round(random.uniform(10, 150), 2)  # 10 ila 150 GEL arası rastgele harcama
    veri.append({'Tarih': tarih, 'Kategori': kategori, 'Harcama_GEL': harcama})

df = pd.DataFrame(veri)
df.to_csv('kutaisi_kaos.csv', index=False)

# CSV'den oku
df2 = pd.read_csv('kutaisi_kaos.csv')

# Toplam harcama
toplam_harcama = df2['Harcama_GEL'].sum()
print(f"Toplam Harcama (GEL): {toplam_harcama:.2f}")

# Kategori bazlı harcama dağılımı
kat_bazli = df2.groupby('Kategori')['Harcama_GEL'].sum()
print("\nKategori Bazlı Harcama Dağılımı (GEL):")
print(kat_bazli)
