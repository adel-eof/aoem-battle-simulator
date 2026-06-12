# Coding Standards

Dokumen ini mendefinisikan pedoman clean architecture dan konvensi coding untuk repository AOEM Battle Simulator.

## Clean Architecture Guidelines

- Pisahkan domain logic dari adapter/infrastruktur:
  - `domain`: entity, value object, aturan bisnis murni.
  - `application`: orchestrasi use case.
  - `infrastructure`: I/O, parser, persistence, external integration.
  - `interface`: CLI/API boundary.
- Domain layer tidak boleh bergantung pada framework atau library I/O.
- Dependency rule: arah ketergantungan selalu menuju layer yang lebih abstrak.
- Gunakan DTO yang jelas untuk lintas boundary; hindari passing dict bebas antar layer.
- Error handling harus eksplisit: gunakan exception bertipe khusus untuk error domain yang dapat dipulihkan.

## Python Conventions

- Gunakan Python 3.12+ dan type hints di seluruh public function.
- Hindari global mutable state.
- Gunakan `pathlib.Path` untuk operasi path/file.
- Public API harus memiliki docstring singkat yang menjelaskan kontrak input/output.
- Gunakan nama yang deskriptif; hindari singkatan yang ambigu.

## Quality Gates

Setiap perubahan harus lulus:
- `ruff check .`
- `mypy src`
- `pytest`

Aturan tambahan:
- Tambahkan test untuk behavior baru atau bug fix.
- Pertahankan test deterministic; hindari ketergantungan ke waktu sistem/random implicit.
- Jangan mengubah API publik tanpa catatan perubahan yang jelas di PR.

## Project Structure Conventions

- Simpan source code di `src/aoemsim/`.
- Simpan test di `tests/` dengan nama file `test_*.py`.
- Simpan kebijakan dan dokumen arsitektur di `docs/`.
- Setiap modul baru harus memiliki batas tanggung jawab tunggal (single responsibility).

## CLI Conventions

- Semua command CLI harus memiliki help text yang jelas.
- Exit code 0 hanya untuk sukses.
- Error pengguna (input invalid) harus menghasilkan pesan human-readable.

## Security & Data Handling

- Parsing YAML wajib mengikuti kebijakan aman di `docs/policies.md`.
- Validasi `schema_version` wajib dilakukan saat ingest data.
- Hindari mengeksekusi konten dinamis dari konfigurasi/data input.
