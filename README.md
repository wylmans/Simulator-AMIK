# Simulator-AMIK

Simulator-AMIK adalah sebuah program game simulasi dari kegiatan sebagai seorang mahasiswa di kampus STMIK AMIK Bandung Program ini berbasis **Python** dan **Pygame** yang dirancang untuk berjalan pada sistem Windows. Program ini ringan dan dapat dijalankan pada perangkat dengan spesifikasi menengah ke bawah.

---

## 📌 Spesifikasi Sistem

Program ini telah diuji dan berjalan dengan baik pada konfigurasi berikut:

* **Sistem Operasi**: Windows 10 (64-bit)
* **Prosesor**: AMD A8-6410 APU
* **RAM**: 8 GB
* **Python**: 3.13.9
* **Pygame**: 2.6.1

---

## 📦 Dependensi

Pastikan dependensi berikut telah terpasang:

* Python **3.13.9**
* Pygame **2.6.1**

---

## 🔽 Mengunduh Proyek

Anda dapat mengunduh proyek ini dengan **dua cara**:

### Opsi 1 — Menggunakan Git (Direkomendasikan)

Pastikan Git sudah terinstal di sistem Anda.

Unduh Git dari:

```
https://git-scm.com/downloads
```

Setelah Git terpasang, jalankan perintah berikut di Command Prompt atau PowerShell:

```bash
git clone https://github.com/wylmans/Simulator-AMIK.git
cd Simulator-AMIK
```

---

### Opsi 2 — Download ZIP (Tanpa Git)

1. Buka halaman repository:

   ```
   https://github.com/wylmans/Simulator-AMIK
   ```
2. Klik tombol **Code** → **Download ZIP**
3. Ekstrak file ZIP ke folder yang diinginkan
4. Masuk ke folder hasil ekstraksi sebelum menjalankan program

---

## 🔧 Instalasi Python

Unduh Python dari situs resmi:

```
https://www.python.org/downloads/
```

Saat instalasi, pastikan:

* ✔ Centang **Add Python to PATH**
* ✔ Gunakan versi **Python 3.13.9**

Verifikasi instalasi:

```bash
python --version
```

Output yang diharapkan:

```
Python 3.13.9
```

---

## 📥 Instalasi Pygame

Gunakan `pip` untuk menginstal Pygame:

```bash
pip install pygame==2.6.1
```

Verifikasi instalasi:

```bash
python -m pygame --version
```

---

## ▶ Menjalankan Program

Masuk ke direktori proyek, lalu jalankan file utama yaitu game.py

```bash
python game.py
```

Jika berhasil, jendela simulasi Pygame akan muncul.

---

## 📂 Struktur Direktori (Contoh)

```text
Simulator-AMIK/
│
├─ assets/        # Asset gambar / audio
├─ src/           # Source code (jika dipisah)
├─ main.py        # Entry point program
├─ README.md
```

---

## 🧪 Catatan Tambahan

* Program tidak memerlukan GPU diskrit
* Gunakan Python dan Pygame pada environment yang sama
* Jika terjadi error `pygame`, pastikan PATH Python sudah benar

---

## 📜 Lisensi

Silakan lihat file `LICENSE` pada repository ini untuk informasi lisensi.

---

## 👤 Pengembang

Dikembangkan oleh **Wylmans Haryamukti**

GitHub:
[https://github.com/wylmans](https://github.com/wylmans)
