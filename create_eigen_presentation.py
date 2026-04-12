#!/usr/bin/env python3
"""
Script untuk membuat presentasi PowerPoint tentang Eigenvalues dan Eigenvectors
Untuk mata kuliah Aljabar Linear - Mahasiswa Teknik Tahun Pertama
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

# Konfigurasi
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Fungsi helper untuk menambah judul slide
def add_title_slide(title, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(41, 84, 209)

    # Judul
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
    title_frame = title_box.text_frame
    title_frame.text = title
    title_frame.word_wrap = True
    title_p = title_frame.paragraphs[0]
    title_p.font.size = Pt(54)
    title_p.font.bold = True
    title_p.font.color.rgb = RGBColor(255, 255, 255)
    title_p.alignment = PP_ALIGN.CENTER

    # Subtitle
    if subtitle:
        subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(1.5))
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = subtitle
        subtitle_frame.word_wrap = True
        subtitle_p = subtitle_frame.paragraphs[0]
        subtitle_p.font.size = Pt(28)
        subtitle_p.font.color.rgb = RGBColor(220, 220, 220)
        subtitle_p.alignment = PP_ALIGN.CENTER

# Fungsi untuk menambah slide konten
def add_content_slide(title, content_items, image_path=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(255, 255, 255)

    # Judul
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
    title_frame = title_box.text_frame
    title_frame.text = title
    title_p = title_frame.paragraphs[0]
    title_p.font.size = Pt(40)
    title_p.font.bold = True
    title_p.font.color.rgb = RGBColor(41, 84, 209)

    # Garis bawah judul
    line_shape = slide.shapes.add_shape(1, Inches(0.5), Inches(1.15), Inches(9), Inches(0))
    line_shape.line.color.rgb = RGBColor(41, 84, 209)
    line_shape.line.width = Pt(2)

    # Konten
    if image_path:
        slide.shapes.add_picture(image_path, Inches(5.5), Inches(1.5), width=Inches(4))
        text_width = 4.8
    else:
        text_width = 9

    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(text_width), Inches(5.5))
    text_frame = content_box.text_frame
    text_frame.word_wrap = True

    for i, item in enumerate(content_items):
        if i > 0:
            text_frame.add_paragraph()
        p = text_frame.paragraphs[i]
        p.text = item
        p.font.size = Pt(18)
        p.font.color.rgb = RGBColor(50, 50, 50)
        p.space_before = Pt(6)
        p.space_after = Pt(6)
        p.level = 0

# Slide 1: Cover
add_title_slide(
    "EIGENVALUES DAN EIGENVECTORS",
    "Aljabar Linear untuk Teknik\nMahasiswa Tahun Pertama"
)

# Slide 2: Apa itu Eigenvalues dan Eigenvectors?
add_content_slide(
    "Definisi: Eigenvalues dan Eigenvectors",
    [
        "• Diberikan matriks A (n × n), vektor non-zero v disebut EIGENVECTOR jika:",
        "  A·v = λ·v",
        "",
        "• λ (lambda) disebut EIGENVALUE (nilai eigen)",
        "",
        "• Interpretasi: Ketika A mengalikan v, hasilnya adalah v yang di-skala oleh λ",
        "  - Jika λ > 1: v diperbesar",
        "  - Jika 0 < λ < 1: v diperkecil",
        "  - Jika λ < 0: v terbalik arah"
    ]
)

# Slide 3: Ilustrasi Geometri
# Membuat diagram ilustrasi
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Subplot 1: Vektor biasa vs eigenvector
A = np.array([[2, 1], [1, 2]])
v = np.array([1, 1])
v_transformed = A @ v

ax1.quiver(0, 0, v[0], v[1], angles='xy', scale_units='xy', scale=1, color='blue', width=0.006, label='v')
ax1.quiver(0, 0, v_transformed[0], v_transformed[1], angles='xy', scale_units='xy', scale=1, color='red', width=0.006, label='A·v')
ax1.set_xlim(-1, 5)
ax1.set_ylim(-1, 5)
ax1.set_aspect('equal')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_title('Vektor Biasa: A·v ≠ λ·v', fontsize=12, fontweight='bold')
ax1.set_xlabel('x')
ax1.set_ylabel('y')

# Subplot 2: Eigenvector
eigenvalues, eigenvectors = np.linalg.eig(A)
v_eigen = eigenvectors[:, 0]  # eigenvector pertama
v_eigen_normalized = v_eigen / np.linalg.norm(v_eigen)
v_eigen_scaled = eigenvalues[0] * v_eigen_normalized

ax2.quiver(0, 0, v_eigen_normalized[0], v_eigen_normalized[1], angles='xy', scale_units='xy', scale=1, color='blue', width=0.006, label='v')
ax2.quiver(0, 0, v_eigen_scaled[0], v_eigen_scaled[1], angles='xy', scale_units='xy', scale=1, color='green', width=0.006, label='λ·v')
ax2.set_xlim(-1, 1.5)
ax2.set_ylim(-1, 1.5)
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_title(f'Eigenvector: A·v = λ·v (λ ≈ {eigenvalues[0]:.2f})', fontsize=12, fontweight='bold')
ax2.set_xlabel('x')
ax2.set_ylabel('y')

plt.tight_layout()
img1 = BytesIO()
plt.savefig(img1, format='png', dpi=150, bbox_inches='tight')
img1.seek(0)
plt.close()

slide = prs.slides.add_slide(prs.slide_layouts[6])
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(255, 255, 255)

title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(0.8))
title_frame = title_box.text_frame
title_frame.text = "Ilustrasi Geometri: Eigenvector"
title_p = title_frame.paragraphs[0]
title_p.font.size = Pt(40)
title_p.font.bold = True
title_p.font.color.rgb = RGBColor(41, 84, 209)

line_shape = slide.shapes.add_shape(1, Inches(0.5), Inches(1.15), Inches(9), Inches(0))
line_shape.line.color.rgb = RGBColor(41, 84, 209)
line_shape.line.width = Pt(2)

slide.shapes.add_picture(img1, Inches(0.8), Inches(1.5), width=Inches(8.4))

# Slide 4: Aplikasi Real-World
add_content_slide(
    "Aplikasi Real-World",
    [
        "1. ANALISIS STRUKTUR (Structural Analysis)",
        "   Menentukan frekuensi natural getaran bangunan/jembatan",
        "",
        "2. COMPUTER GRAPHICS",
        "   Transformasi 3D, rotasi, skalasi objek",
        "",
        "3. MACHINE LEARNING",
        "   Principal Component Analysis (PCA) untuk reduksi dimensi",
        "",
        "4. SISTEM DINAMIS",
        "   Analisis stabilitas sistem kontrol",
        "",
        "5. FISIKA KUANTUM",
        "   Energi partikel dalam mekanika kuantum"
    ]
)

# Slide 5: Cara Menghitung Eigenvalues
add_content_slide(
    "Langkah Menghitung Eigenvalues",
    [
        "LANGKAH 1: Bentuk persamaan karakteristik",
        "   det(A - λI) = 0",
        "",
        "   Dimana:",
        "   • A adalah matriks (n × n)",
        "   • λ adalah eigenvalue (yang dicari)",
        "   • I adalah matriks identitas",
        "",
        "LANGKAH 2: Hitung determinan",
        "   Selesaikan det(A - λI) = 0",
        "",
        "LANGKAH 3: Dapatkan polinomial karakteristik",
        "   Polynomial degree n dengan akar-akarnya adalah eigenvalues"
    ]
)

# Slide 6: Cara Menghitung Eigenvectors
add_content_slide(
    "Langkah Menghitung Eigenvectors",
    [
        "LANGKAH 1: Untuk setiap eigenvalue λ",
        "",
        "LANGKAH 2: Selesaikan sistem persamaan linear homogen",
        "   (A - λI)·v = 0",
        "",
        "   Dimana v adalah eigenvector yang dicari",
        "",
        "LANGKAH 3: Cari basis dari null space (A - λI)",
        "",
        "LANGKAH 4: Setiap vektor non-zero dari solusi adalah eigenvector",
        "   yang bersesuaian dengan eigenvalue λ"
    ]
)

# Slide 7: Contoh Soal 1 (Mudah)
add_content_slide(
    "Contoh Soal 1: Matriks 2×2 (Mudah)",
    [
        "Diberikan matriks A = [3  1]",
        "                       [1  3]",
        "",
        "Carilah eigenvalues dari matriks A!"
    ]
)

# Slide 8: Solusi Contoh 1 - Step 1
add_content_slide(
    "Solusi Contoh 1 - Langkah 1: Bentuk Persamaan Karakteristik",
    [
        "det(A - λI) = 0",
        "",
        "A - λI = [3-λ    1  ]",
        "         [ 1   3-λ ]",
        "",
        "det(A - λI) = (3-λ)(3-λ) - 1·1",
        "             = (3-λ)² - 1",
        "             = 9 - 6λ + λ² - 1",
        "             = λ² - 6λ + 8"
    ]
)

# Slide 9: Solusi Contoh 1 - Step 2
add_content_slide(
    "Solusi Contoh 1 - Langkah 2: Selesaikan Persamaan",
    [
        "λ² - 6λ + 8 = 0",
        "",
        "Faktorisasi:",
        "(λ - 2)(λ - 4) = 0",
        "",
        "Jadi: λ₁ = 2  dan  λ₂ = 4",
        "",
        "✓ EIGENVALUES dari matriks A adalah 2 dan 4"
    ]
)

# Slide 10: Contoh Soal 2 - Cari Eigenvector
add_content_slide(
    "Contoh Soal 2: Cari Eigenvector untuk Contoh 1",
    [
        "Untuk matriks A = [3  1]  dengan eigenvalues λ₁ = 2, λ₂ = 4",
        "                   [1  3]",
        "",
        "Carilah eigenvector yang bersesuaian dengan setiap eigenvalue!"
    ]
)

# Slide 11: Solusi Contoh 2 - Untuk λ₁ = 2
add_content_slide(
    "Solusi Contoh 2 - Eigenvector untuk λ₁ = 2",
    [
        "Selesaikan: (A - 2I)v = 0",
        "",
        "(A - 2I) = [3-2   1 ] = [1  1]",
        "           [ 1  3-2]   [1  1]",
        "",
        "[1  1][v₁]   [0]",
        "[1  1][v₂] = [0]",
        "",
        "Persamaan: v₁ + v₂ = 0  →  v₂ = -v₁",
        "",
        "Pilih v₁ = 1, maka v₂ = -1",
        "",
        "✓ Eigenvector untuk λ₁ = 2:  v₁ = [ 1 ]",
        "                                   [-1]"
    ]
)

# Slide 12: Solusi Contoh 2 - Untuk λ₂ = 4
add_content_slide(
    "Solusi Contoh 2 - Eigenvector untuk λ₂ = 4",
    [
        "Selesaikan: (A - 4I)v = 0",
        "",
        "(A - 4I) = [3-4   1 ] = [-1  1]",
        "           [ 1  3-4]   [ 1 -1]",
        "",
        "[-1  1][v₁]   [0]",
        "[ 1 -1][v₂] = [0]",
        "",
        "Persamaan: -v₁ + v₂ = 0  →  v₂ = v₁",
        "",
        "Pilih v₁ = 1, maka v₂ = 1",
        "",
        "✓ Eigenvector untuk λ₂ = 4:  v₂ = [1]",
        "                                   [1]"
    ]
)

# Slide 13: Verifikasi Hasil
add_content_slide(
    "Verifikasi Hasil",
    [
        "Cek untuk λ₁ = 2, v₁ = [1, -1]ᵀ:",
        "",
        "A·v₁ = [3  1][1 ]  = [3-1 ] = [ 2 ]  = 2[1 ]  ✓",
        "       [1  3][-1]    [1-3]    [-2]      [-1]",
        "",
        "Cek untuk λ₂ = 4, v₂ = [1, 1]ᵀ:",
        "",
        "A·v₂ = [3  1][1] = [3+1] = [4] = 4[1] ✓",
        "       [1  3][1]   [1+3]   [4]     [1]",
        "",
        "✓ Hasil terverifikasi benar!"
    ]
)

# Slide 14: Contoh Soal 3 (Tingkat Sedang)
add_content_slide(
    "Contoh Soal 3: Matriks 3×3 (Tingkat Sedang)",
    [
        "Diberikan matriks A = [ 2  -1   0]",
        "                       [-1   2  -1]",
        "                       [ 0  -1   2]",
        "",
        "Carilah satu eigenvalue dari matriks A!"
    ]
)

# Slide 15: Solusi Contoh 3
add_content_slide(
    "Solusi Contoh 3: Bentuk Persamaan Karakteristik",
    [
        "det(A - λI) = 0",
        "",
        "det([2-λ  -1    0 ])",
        "   [-1   2-λ  -1 ])",
        "   [ 0   -1  2-λ ])",
        "",
        "Ekspansi sepanjang baris pertama:",
        "= (2-λ)·det([2-λ  -1]) - (-1)·det([-1  -1])",
        "          [ -1  2-λ]        [ 0  2-λ]",
        "",
        "= (2-λ)[(2-λ)² - 1] + 1[-(2-λ)]",
        "= (2-λ)³ - (2-λ) - (2-λ)",
        "= (2-λ)³ - 2(2-λ)"
    ]
)

# Slide 16: Solusi Contoh 3 Lanjutan
add_content_slide(
    "Solusi Contoh 3 - Lanjutan",
    [
        "(2-λ)³ - 2(2-λ) = 0",
        "",
        "Faktorisasi: (2-λ)[(2-λ)² - 2] = 0",
        "",
        "Solusi:",
        "1) 2-λ = 0  →  λ₁ = 2",
        "",
        "2) (2-λ)² - 2 = 0",
        "   (2-λ)² = 2",
        "   2-λ = ±√2",
        "   λ₂ = 2-√2 ≈ 0.586",
        "   λ₃ = 2+√2 ≈ 3.414",
        "",
        "✓ Eigenvalues: 2, 2-√2, 2+√2"
    ]
)

# Slide 17: Ringkasan Proses
add_content_slide(
    "Ringkasan: Proses Menghitung Eigenvalues dan Eigenvectors",
    [
        "1. CARI EIGENVALUES:",
        "   • Bentuk det(A - λI) = 0",
        "   • Selesaikan polinomial karakteristik",
        "",
        "2. UNTUK SETIAP EIGENVALUE λᵢ:",
        "   • Bentuk matriks (A - λᵢI)",
        "   • Selesaikan (A - λᵢI)v = 0",
        "   • Eigenvector adalah solusi non-zero",
        "",
        "3. VERIFIKASI:",
        "   • Cek: Av = λv untuk setiap pasangan"
    ]
)

# Slide 18: Penugasan Rumah - Soal 1
add_content_slide(
    "PENUGASAN RUMAH (Homework)",
    [
        "SOAL 1: Matriks 2×2",
        "",
        "Diberikan A = [4  2]",
        "              [2  1]",
        "",
        "a) Carilah eigenvalues dari matriks A",
        "",
        "b) Carilah eigenvector untuk setiap eigenvalue",
        "",
        "c) Verifikasi hasil Anda (buktikan Av = λv)"
    ]
)

# Slide 19: Penugasan Rumah - Soal 2
add_content_slide(
    "PENUGASAN RUMAH (Lanjutan)",
    [
        "SOAL 2: Aplikasi Real-World",
        "",
        "Sistem pegas dengan matrik stiffness A = [6  -2]",
        "                                         [-2  4]",
        "",
        "Eigenvalues dari matriks ini mewakili frekuensi natural kuadrat (ω²)",
        "dari sistem getaran dua derajat kebebasan.",
        "",
        "a) Tentukan eigenvalues",
        "",
        "b) Hitung frekuensi natural: f = √λ/(2π)",
        "",
        "c) Interpretasikan hasil fisiknya"
    ]
)

# Slide 20: Penugasan Rumah - Soal 3
add_content_slide(
    "PENUGASAN RUMAH (Lanjutan)",
    [
        "SOAL 3: Matriks 3×3",
        "",
        "Diberikan A = [3  0  1]",
        "              [0  2  0]",
        "              [1  0  3]",
        "",
        "a) Carilah semua eigenvalues",
        "",
        "b) Carilah eigenvector untuk λ = 2",
        "",
        "c) Berapa dimensi eigenspace untuk λ = 2?"
    ]
)

# Slide 21: Kesimpulan
add_title_slide(
    "Kesimpulan",
    "Eigenvalues dan Eigenvectors adalah konsep fundamental\nyang penting dalam matematika terapan dan teknik"
)

# Slide 22: Referensi
add_content_slide(
    "Referensi dan Sumber Belajar",
    [
        "1. Lay, D. C. (2016). Linear Algebra and Its Applications",
        "   Pearson Education",
        "",
        "2. Strang, G. (2009). Introduction to Linear Algebra",
        "   Wellesley-Cambridge Press",
        "",
        "3. 3Blue1Brown - Essence of Linear Algebra (YouTube)",
        "   Channel: 3Blue1Brown",
        "",
        "4. Khan Academy - Linear Algebra",
        "   https://www.khanacademy.org/math/linear-algebra",
        "",
        "Instruktur: [Nama Dosen]",
        "Kampus: [Universitas/Institusi]"
    ]
)

# Simpan presentasi
output_file = "/home/user/Proyek-Modul-PLC-Kelas-A-dan-B/Eigenvalues_Eigenvectors_Presentation.pptx"
prs.save(output_file)
print(f"✓ Presentasi berhasil dibuat: {output_file}")
print(f"✓ Total slides: {len(prs.slides)}")
