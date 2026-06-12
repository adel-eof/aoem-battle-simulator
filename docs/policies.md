# Engineering Policies

Dokumen ini mendefinisikan kebijakan wajib lintas milestone. Ketiga aturan di bawah bersifat mandatory, bukan rekomendasi.

## 1. RNG Harus Seeded + Roll Counter

Aturan operasional:
- Semua sumber random engine wajib menggunakan seed eksplisit (tidak boleh implicit system seed).
- Setiap operasi RNG harus menghasilkan event yang menyimpan minimal:
  - `roll_index` (counter monotonic, mulai dari 0 atau 1 secara konsisten)
  - `source` (modul/fitur yang melakukan roll)
  - `result` (nilai random yang dihasilkan)
- Counter harus naik tepat satu per roll dan tidak boleh reset di tengah simulasi battle.
- Reproducibility wajib: untuk seed dan input simulasi yang sama, urutan hasil RNG harus identik byte-for-byte pada log event.

Implementasi minimum yang diharapkan pada milestone berikutnya:
- Satu abstraction RNG terpusat (mis. `RngService`) yang menerima seed saat inisialisasi.
- API RNG tidak expose `random.*` global langsung.
- Tersedia mekanisme export/inspect trace RNG per run.

## 2. YAML Wajib `safe_load` / `SafeLoader`

Aturan operasional:
- Parsing YAML hanya boleh memakai API aman: `yaml.safe_load` atau turunan `yaml.SafeLoader`.
- Dilarang memakai loader tidak aman (contoh: `yaml.load` tanpa SafeLoader) yang dapat mengeksekusi konstruktor objek Python arbitrer.
- Review code wajib menolak setiap penggunaan API parsing YAML yang tidak aman.

Checklist validasi:
- Tidak ada call site `yaml.load(` tanpa argumen loader aman.
- Jika custom loader dipakai, base class loader harus `yaml.SafeLoader`.

## 3. Metadata `schema_version` Wajib di Root Dokumen

Aturan operasional:
- Setiap dokumen data domain YAML wajib memiliki field root `schema_version`.
- Ingest data wajib memvalidasi versi schema sebelum data dipakai engine.
- Bila versi tidak kompatibel, sistem harus fail-fast dengan error jelas yang memuat:
  - versi dokumen
  - versi yang didukung
  - saran tindakan (upgrade/migration)

Contoh pesan error:
- `Unsupported schema_version: 3.0. Supported range: 1.x - 2.x.`

## Target Performa Baseline

Target performa minimum:
- 1000 simulasi battle 3v3 harus selesai dalam <= 30 detik pada environment pengembangan standar.

Catatan:
- Benchmark harus dijalankan secara reproducible (seed tetap, input tetap).
- Bila target tidak tercapai, PR wajib menyertakan analisis bottleneck sebelum merge.
