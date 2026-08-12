-- =====================================================
-- DATABASE SISTEM ANALISIS PANGAN LOKAL
-- =====================================================

-- 1. Buat database (jalankan sebagai superuser)
-- CREATE DATABASE pangan_lokal;
-- \c pangan_lokal

-- 2. Hapus tabel jika sudah ada (opsional, hati-hati)
DROP TABLE IF EXISTS data_produksi CASCADE;
DROP TABLE IF EXISTS komoditas CASCADE;
DROP TABLE IF EXISTS daerah CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 3. Tabel Users
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'petugas', 'dinas')),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabel Daerah / Kota
CREATE TABLE daerah (
    id              SERIAL PRIMARY KEY,
    nama_daerah     VARCHAR(100) NOT NULL,
    pulau           VARCHAR(50) NOT NULL,
    latitude        DECIMAL(10, 6),
    longitude       DECIMAL(10, 6),
    keterangan      TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabel Komoditas Pangan
CREATE TABLE komoditas (
    id              SERIAL PRIMARY KEY,
    nama_komoditas  VARCHAR(100) NOT NULL,
    kategori        VARCHAR(50),
    deskripsi       TEXT,
    is_lokal        BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabel Data Produksi
CREATE TABLE data_produksi (
    id                  SERIAL PRIMARY KEY,
    daerah_id           INTEGER NOT NULL REFERENCES daerah(id) ON DELETE CASCADE,
    komoditas_id        INTEGER NOT NULL REFERENCES komoditas(id) ON DELETE CASCADE,
    tahun               INTEGER NOT NULL,
    produksi_ton        DECIMAL(12, 2),
    luas_ha             DECIMAL(12, 2),
    produktivitas       DECIMAL(8, 2),
    curah_hujan_mm      DECIMAL(10, 2),
    suhu_c              DECIMAL(5, 2),
    indeks_kearifan     INTEGER CHECK (indeks_kearifan BETWEEN 1 AND 5),
    status_gagal_panen  INTEGER CHECK (status_gagal_panen IN (0, 1)),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Index untuk performa
CREATE INDEX idx_produksi_daerah ON data_produksi(daerah_id);
CREATE INDEX idx_produksi_komoditas ON data_produksi(komoditas_id);
CREATE INDEX idx_produksi_tahun ON data_produksi(tahun);
CREATE INDEX idx_daerah_pulau ON daerah(pulau);

-- =====================================================
-- DATA AWAL (SAMPLE)
-- =====================================================

-- User Admin default
-- Username: admin
-- Password: admin123
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', '$2b$12$8K1p/a0dL1LXMIgoEDFrwOfMQs1qKqJqKqJqKqJqKqJqKqJqKqJqKq', 'Administrator Sistem', 'admin');

-- Catatan: Hash di atas adalah contoh. 
-- Setelah aplikasi berjalan, sebaiknya buat ulang user admin melalui form Register 
-- atau gunakan script Python untuk generate hash yang benar.

-- Sample Daerah (dengan koordinat)
INSERT INTO daerah (nama_daerah, pulau, latitude, longitude, keterangan) VALUES
('Palembang', 'Sumatra', -2.990934, 104.756554, 'Sample Sumatra Selatan'),
('Medan', 'Sumatra', 3.595196, 98.672226, 'Sample Sumatra Utara'),
('Surabaya', 'Jawa', -7.257472, 112.752088, 'Sample Jawa Timur'),
('Yogyakarta', 'Jawa', -7.795580, 110.369492, 'Sample DI Yogyakarta'),
('Kupang', 'NTT', -10.177200, 123.598000, 'Sample Nusa Tenggara Timur'),
('Banjarbaru', 'Kalimantan', -3.457242, 114.810318, 'Sample Kalimantan Selatan'),
('Makassar', 'Sulawesi', -5.147665, 119.432732, 'Sample Sulawesi Selatan'),
('Merauke', 'Papua', -8.496100, 140.395000, 'Sample Papua Selatan');

-- Sample Komoditas Lokal
INSERT INTO komoditas (nama_komoditas, kategori, deskripsi, is_lokal) VALUES
('Padi Lokal Gambut', 'Padi-padian', 'Padi lokal lahan gambut', TRUE),
('Jagung Lokal', 'Jagung', 'Jagung lokal tahan kering', TRUE),
('Ubi Jalar', 'Umbi-umbian', 'Ubi jalar lokal', TRUE),
('Sagu', 'Sagu', 'Sagu tradisional Papua & Maluku', TRUE),
('Padi Gogo', 'Padi-padian', 'Padi gogo lahan kering', TRUE),
('Sorgum', 'Padi-padian', 'Sorgum lokal NTT', TRUE),
('Keladi / Talas', 'Umbi-umbian', 'Talas lokal Papua', TRUE),
('Ubi Kayu', 'Umbi-umbian', 'Ubi kayu lokal', TRUE);

-- =====================================================
-- SELESAI
-- =====================================================