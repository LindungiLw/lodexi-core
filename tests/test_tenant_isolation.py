def test_health_check(client):
    """Ensure service health check endpoint responds with 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_auth_rejection(client):
    """Requests without a valid API Key must be rejected with 401."""
    # Missing API Key
    resp_missing = client.post("/v1/search", json={"query": "test query"})
    assert resp_missing.status_code == 401

    # Invalid API Key
    resp_invalid = client.post(
        "/v1/search",
        json={"query": "test query"},
        headers={"X-API-Key": "invalid_random_key_999"},
    )
    assert resp_invalid.status_code == 401


def test_cross_tenant_isolation(client, headers_jiulibrary, headers_staffportal):
    """Strict test: Tenant A (jiulibrary) data must NEVER be accessible to Tenant B (staff_portal)."""
    
    # 1. Ingest confidential book catalog in jiulibrary
    doc_library = {
        "external_id": "book_hist_001",
        "title": "Buku Sejarah Peradaban Kuno dan Orde Baru",
        "content": (
            "Buku ini membahas sejarah politik dan transisi kekuasaan peradaban kuno "
            "serta catatan tahanan politik di era Orde Baru Indonesia secara komprehensif."
        ),
        "category": "sejarah",
    }
    resp_ingest_lib = client.post("/v1/documents", json=doc_library, headers=headers_jiulibrary)
    assert resp_ingest_lib.status_code == 201
    assert resp_ingest_lib.json()["tenant_id"] == "jiulibrary"

    # 2. Ingest internal HR SOP in staff_portal
    doc_sop = {
        "external_id": "sop_hr_021",
        "title": "SOP-021: Prosedur Pengajuan Izin Cuti dan Lembur",
        "content": (
            "Karyawan berhak mengajukan izin cuti tahunan maksimal 12 hari kerja per tahun. "
            "Pengajuan cuti wajib diajukan minimal 3 hari sebelum tanggal cuti melalui atasan langsung."
        ),
        "category": "kepegawaian",
    }
    resp_ingest_sop = client.post("/v1/documents", json=doc_sop, headers=headers_staffportal)
    assert resp_ingest_sop.status_code == 201
    assert resp_ingest_sop.json()["tenant_id"] == "staff_portal"

    # 3. jiulibrary searches for its own book -> MUST FIND IT
    search_lib = client.post(
        "/v1/search",
        json={"query": "sejarah peradaban kuno orde baru", "limit": 5},
        headers=headers_jiulibrary,
    )
    assert search_lib.status_code == 200
    data_lib = search_lib.json()
    assert data_lib["tenant_id"] == "jiulibrary"
    assert data_lib["total_found"] > 0
    assert data_lib["results"][0]["external_id"] == "book_hist_001"

    # 4. CRITICAL: staff_portal searches for the exact same book query -> MUST RETURN ZERO
    search_leak_check = client.post(
        "/v1/search",
        json={"query": "sejarah peradaban kuno orde baru", "limit": 5},
        headers=headers_staffportal,
    )
    assert search_leak_check.status_code == 200
    data_leak = search_leak_check.json()
    assert data_leak["tenant_id"] == "staff_portal"
    # Verification: Zero cross-tenant leakage!
    found_external_ids = [r["external_id"] for r in data_leak["results"]]
    assert "book_hist_001" not in found_external_ids

    # 5. Reverse check: jiulibrary searches for HR SOP -> MUST NOT FIND IT
    reverse_check = client.post(
        "/v1/search",
        json={"query": "syarat pengajuan cuti tahunan", "limit": 5},
        headers=headers_jiulibrary,
    )
    assert reverse_check.status_code == 200
    lib_leak_ids = [r["external_id"] for r in reverse_check.json()["results"]]
    assert "sop_hr_021" not in lib_leak_ids

    # 6. Ask QA endpoint isolation check:
    # staff_portal asks about leave -> must ground on SOP
    ask_sop = client.post(
        "/v1/ask",
        json={"question": "Berapa hari maksimal cuti tahunan karyawan?"},
        headers=headers_staffportal,
    )
    assert ask_sop.status_code == 200
    assert ask_sop.json()["tenant_id"] == "staff_portal"
    assert len(ask_sop.json()["citations"]) > 0
    assert ask_sop.json()["citations"][0]["external_id"] == "sop_hr_021"

    # jiulibrary asks about leave -> MUST NOT see or cite the SOP
    ask_cross = client.post(
        "/v1/ask",
        json={"question": "Berapa hari maksimal cuti tahunan karyawan?"},
        headers=headers_jiulibrary,
    )
    assert ask_cross.status_code == 200
    assert ask_cross.json()["tenant_id"] == "jiulibrary"
    cross_citations = [c["external_id"] for c in ask_cross.json()["citations"]]
    assert "sop_hr_021" not in cross_citations
