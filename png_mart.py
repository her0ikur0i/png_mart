import os
import requests
from bs4 import BeautifulSoup
import sys
import time

# Fungsi untuk mendownload gambar
def download_image(url, filename):
    retries = 3  # Jumlah percobaan unduh ulang jika terjadi kesalahan koneksi
    while retries > 0:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    file.write(response.content)
                    print(f"Gambar {filename} berhasil diunduh.")
                    return True
            else:
                print(f"Gagal mengunduh gambar {filename}. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Terjadi kesalahan saat mengunduh gambar {filename}: {str(e)}")
            retries -= 1
            print(f"Melakukan percobaan unduh ulang. Percobaan tersisa: {retries}")
            time.sleep(1)  # Tunggu sebelum mencoba unduh ulang
    return False

# URL situs yang akan di-scraper
site = 'https://www.pngmart.com/sitemap.xml'

# Mendapatkan konten XML dari situs
test_site = requests.get(site)
xml = test_site.text

# Parsing XML menggunakan BeautifulSoup
soup = BeautifulSoup(xml, 'xml')

# Mencari semua elemen <loc> untuk mendapatkan link
xml_list = [xml.text for xml in soup.find_all('loc') if 'posts' in xml.text]

# Inisialisasi jumlah gambar yang akan di-download
num_images_to_download = 3
images_per_folder = 1
downloaded_images_count = 0
time.sleep(5)

# Direktori penyimpanan gambar
download_directory = os.path.dirname(os.path.abspath(__file__))
main_folder = 'Downloaded_Images'
download_directory = os.path.join(download_directory, main_folder)

# Membuat folder utama untuk menyimpan gambar
os.makedirs(download_directory, exist_ok=True)

# Membuat folder-folder untuk menyimpan gambar di dalam folder utama
for i in range(1, num_images_to_download + 1):
    folder_name = f"Folder_{i}"
    folder_path = os.path.join(download_directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)

# Mendapatkan link gambar dari setiap link post
for post_link in xml_list:
    test_xml = requests.get(post_link)
    soup = BeautifulSoup(test_xml.text, 'xml')
    img_list = [img.text for img in soup.find_all('loc') if 'image' in img.text]
    
    # Download gambar dari setiap link gambar
    for img_link in img_list:
        if downloaded_images_count >= num_images_to_download:
            print(f"Jumlah maksimum gambar yang diunduh ({num_images_to_download}) telah tercapai. Berhenti mengunduh.")
            sys.exit()  # Menghentikan program
        
        # Mendapatkan folder penyimpanan gambar
        folder_index = (downloaded_images_count % num_images_to_download) + 1
        folder_name = f"Folder_{folder_index}"
        folder_path = os.path.join(download_directory, folder_name)

        image_response = requests.get(img_link)
        img_soup = BeautifulSoup(image_response.text, 'html.parser')
        png_link = img_soup.find('a', {'class':'download'})['href']
        img_id = img_link.split('/')[-1]
        img_name = png_link.split('/')[-1]
        img_title = f"{img_id}-{img_name}"
        
        # Mendapatkan jalur lengkap untuk menyimpan gambar
        save_path = os.path.join(folder_path, img_title)
        
        # Memeriksa apakah gambar sudah diunduh sebelumnya
        if os.path.exists(save_path):
            print(f"Gambar {save_path} sudah diunduh sebelumnya.")
            continue
        
        # Memanggil fungsi download_image
        success = download_image(png_link, save_path)
        if success:
            downloaded_images_count += 1

        # Memeriksa apakah sudah mencapai jumlah maksimal gambar yang diunduh
        if downloaded_images_count >= num_images_to_download:
            print(f"Jumlah maksimum gambar yang diunduh ({num_images_to_download}) telah tercapai. Berhenti mengunduh.")
            sys.exit()  # Menghentikan program

print("Proses pengunduhan selesai.")
