from backend.app.services.digest import aggregate_sources, normalize_url


def _item(source, title, url="", score=0):
    base = {"source": source, "title": title, "score": score}
    if url is not None:
        base["url"] = url
    return base


def test_aggregate_three_sources_interleaved():
    hn = [_item("HN", f"H{i}", f"https://hn.com/{i}") for i in range(2)]
    tc = [_item("TC", f"T{i}", f"https://tc.com/{i}") for i in range(2)]
    ar = [_item("AR", f"A{i}", f"https://ar.com/{i}") for i in range(2)]

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H0", "T0", "A0", "H1", "T1", "A1"]


def test_aggregate_one_source_empty():
    hn = [_item("HN", "H0", "https://hn.com/0")]
    tc = []
    ar = [_item("AR", "A0", "https://ar.com/0")]

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H0", "A0"]


def test_aggregate_two_sources_empty():
    hn = [_item("HN", "H0", "https://hn.com/0")]
    tc = []
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H0"]


def test_aggregate_all_sources_empty():
    result = aggregate_sources([], [], [])
    assert result == []


def test_aggregate_uneven_source_lengths():
    hn = [_item("HN", f"H{i}", f"https://hn.com/{i}") for i in range(3)]
    tc = [_item("TC", f"T{i}", f"https://tc.com/{i}") for i in range(2)]
    ar = [_item("AR", f"A{i}", f"https://ar.com/{i}") for i in range(1)]

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H0", "T0", "A0", "H1", "T1", "H2"]


def test_aggregate_deduplicate_cross_source():
    hn = [_item("HN", "H0", "https://example.com/x")]
    tc = [_item("TC", "T0", "HTTPS://Example.COM/x")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1
    assert result[0]["title"] == "H0"


def test_aggregate_blank_urls_not_deduplicated():
    hn = [_item("HN", "H1", ""), _item("HN", "H2", "")]
    tc = [_item("TC", "T1", "")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H1", "T1", "H2"]


def test_aggregate_missing_url_key():
    hn = [{"source": "HN", "title": "H1", "score": 0}]
    tc = [{"source": "TC", "title": "T1", "score": 0}]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H1", "T1"]


def test_aggregate_preserves_internal_order():
    hn = [_item("HN", f"H{i}", f"https://hn.com/{i}") for i in range(3)]
    tc = []
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["H0", "H1", "H2"]


def test_aggregate_does_not_mutate_inputs():
    hn = [_item("HN", "H0", "https://hn.com/0")]
    tc = [_item("TC", "T0", "https://tc.com/0")]
    ar = [_item("AR", "A0", "https://ar.com/0")]
    hn_snapshot = list(hn)
    tc_snapshot = list(tc)
    ar_snapshot = list(ar)

    aggregate_sources(hn, tc, ar)

    assert hn == hn_snapshot
    assert tc == tc_snapshot
    assert ar == ar_snapshot


def test_normalize_url_trims_whitespace():
    assert normalize_url("  https://example.com/x  ") == "https://example.com/x"


def test_normalize_url_case_insensitive_scheme_host():
    assert normalize_url("HTTPS://Example.COM/x") == "https://example.com/x"


def test_normalize_url_removes_fragment():
    assert normalize_url("https://example.com/x#frag") == "https://example.com/x"


def test_normalize_url_removes_trailing_slash_non_root():
    assert normalize_url("https://example.com/path/") == "https://example.com/path"
    assert normalize_url("https://example.com/") == "https://example.com/"


def test_normalize_url_preserves_query():
    assert (
        normalize_url("https://example.com/x?q=1&b=2#frag")
        == "https://example.com/x?q=1&b=2"
    )


def test_aggregate_dedup_trailing_slash_variation():
    hn = [_item("HN", "H0", "https://example.com/path/")]
    tc = [_item("TC", "T0", "https://example.com/path")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1


def test_aggregate_dedup_fragment_variation():
    hn = [_item("HN", "H0", "https://example.com/x#frag1")]
    tc = [_item("TC", "T0", "https://example.com/x#frag2")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1


def test_aggregate_dedup_case_variation():
    hn = [_item("HN", "H0", "HTTPS://Example.COM/x#frag")]
    tc = [_item("TC", "T0", "https://example.com/x")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1


def test_aggregate_dedup_title_cross_source():
    hn = [_item("HN", "Same Title", "https://hn.com/1")]
    tc = [_item("TC", "Same Title", "https://tc.com/1")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1
    assert result[0]["title"] == "Same Title"


def test_aggregate_dedup_title_case_variation():
    hn = [_item("HN", "AI IS GREAT", "https://hn.com/1")]
    tc = [_item("TC", "ai is great", "https://tc.com/1")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert len(result) == 1


def test_aggregate_blank_urls_with_duplicate_titles_deduped():
    hn = [_item("HN", "Shared", ""), _item("HN", "Unique", "")]
    tc = [_item("TC", "Shared", "")]
    ar = []

    result = aggregate_sources(hn, tc, ar)

    assert [item["title"] for item in result] == ["Shared", "Unique"]
