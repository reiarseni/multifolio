from app.services.referrer_analyzer import (
    extract_domain,
    get_domain_info,
    is_notable_referrer,
)


def test_extract_domain_full_url():
    assert extract_domain("https://github.com/user/repo") == "github.com"
    assert extract_domain("http://linkedin.com/in/user") == "linkedin.com"
    assert extract_domain("https://www.google.com/search?q=test") == "www.google.com"


def test_extract_domain_none():
    assert extract_domain(None) is None


def test_extract_domain_empty():
    assert extract_domain("") is None


def test_extract_domain_no_protocol():
    assert extract_domain("github.com") is None
    assert extract_domain("just-a-string") is None


def test_is_notable_referrer_corporate():
    assert is_notable_referrer("https://google.com") is True
    assert is_notable_referrer("https://microsoft.com") is True
    assert is_notable_referrer("https://amazon.com") is True


def test_is_notable_referrer_social():
    assert is_notable_referrer("https://linkedin.com/in/user") is True
    assert is_notable_referrer("https://github.com/org/repo") is True


def test_is_notable_referrer_unknown():
    assert is_notable_referrer("https://some-random-blog.com") is False
    assert is_notable_referrer("https://localhost:3000") is False


def test_is_notable_referrer_none():
    assert is_notable_referrer(None) is False


def test_is_notable_referrer_empty():
    assert is_notable_referrer("") is False


def test_get_domain_info_corporate():
    info = get_domain_info("google.com")
    assert info["domain"] == "google.com"
    assert info["is_corporate"] is True
    assert info["category"] == "corporate"


def test_get_domain_info_known_not_corporate():
    info = get_domain_info("myspace.com")
    assert info["domain"] == "myspace.com"
    assert info["is_corporate"] is False
    assert info["category"] == "unknown"


def test_get_domain_info_unknown():
    info = get_domain_info("random-site.com")
    assert info["domain"] == "random-site.com"
    assert info["is_corporate"] is False
    assert info["category"] == "unknown"


def test_get_domain_info_none():
    info = get_domain_info(None)
    assert info["domain"] is None
    assert info["is_corporate"] is False
    assert info["category"] == "unknown"
