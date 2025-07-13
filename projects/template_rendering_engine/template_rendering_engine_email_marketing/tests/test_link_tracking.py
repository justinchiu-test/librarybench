"""Tests for link tracking functionality."""

from pytemplate.link_tracking import (
    LinkTracker,
    LinkTrackingConfig,
    UTMParams,
)


class TestLinkTracker:
    """Test link tracking and UTM parameter injection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = LinkTracker()

    def test_basic_utm_injection(self):
        """Test basic UTM parameter injection."""
        utm_params = UTMParams(
            utm_source="newsletter", utm_medium="email", utm_campaign="summer_sale"
        )

        html = '<a href="https://example.com/products">Shop Now</a>'

        result = self.tracker.track_links(html, utm_params)

        assert "utm_source=newsletter" in result
        assert "utm_medium=email" in result
        assert "utm_campaign=summer_sale" in result

    def test_preserve_existing_parameters(self):
        """Test preservation of existing URL parameters."""
        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="test"
        )

        html = '<a href="https://example.com/page?id=123&ref=abc">Link</a>'

        result = self.tracker.track_links(html, utm_params)

        assert "id=123" in result
        assert "ref=abc" in result
        assert "utm_source=email" in result

    def test_multiple_links(self):
        """Test tracking multiple links."""
        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="multi"
        )

        html = """
        <a href="https://example.com">Home</a>
        <a href="https://example.com/products">Products</a>
        <a href="https://example.com/contact">Contact</a>
        """

        result = self.tracker.track_links(html, utm_params)

        assert result.count("utm_source=email") == 3
        assert len(self.tracker.tracked_links) == 3

    def test_exclude_domains(self):
        """Test domain exclusion from tracking."""
        config = LinkTrackingConfig(exclude_domains=["internal.com", "localhost"])
        tracker = LinkTracker(config)

        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="test"
        )

        html = """
        <a href="https://example.com">Track this</a>
        <a href="https://internal.com/page">Don't track this</a>
        <a href="http://localhost:8080">Don't track this either</a>
        """

        result = tracker.track_links(html, utm_params)

        assert "example.com" in result and "utm_source=email" in result
        assert (
            "internal.com" in result
            and "utm_source" not in result.split("internal.com")[1].split(">")[0]
        )
        assert (
            "localhost" in result
            and "utm_source" not in result.split("localhost")[1].split(">")[0]
        )

    def test_non_http_links(self):
        """Test handling of non-HTTP links."""
        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="test"
        )

        html = """
        <a href="mailto:info@example.com">Email us</a>
        <a href="tel:+1234567890">Call us</a>
        <a href="https://example.com">Visit us</a>
        """

        result = self.tracker.track_links(html, utm_params)

        assert "mailto:info@example.com" in result
        assert "utm_source" not in result.split("mailto:")[1].split(">")[0]
        assert "tel:+1234567890" in result
        assert "https://example.com" in result and "utm_source=email" in result

    def test_anchor_preservation(self):
        """Test preservation of URL anchors."""
        config = LinkTrackingConfig(preserve_anchors=True)
        tracker = LinkTracker(config)

        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="test"
        )

        html = '<a href="https://example.com/page#section2">Jump to section</a>'

        result = tracker.track_links(html, utm_params)

        assert "#section2" in result
        assert "utm_source=email" in result

    def test_redirect_tracking(self):
        """Test redirect-based tracking."""
        config = LinkTrackingConfig(tracking_domain="https://track.example.com")
        tracker = LinkTracker(config)

        html = '<a href="https://example.com/products">Shop</a>'

        result = tracker.track_links(html)

        assert "https://track.example.com/track" in result
        assert "url=https%3A%2F%2Fexample.com%2Fproducts" in result

    def test_hash_urls_security(self):
        """Test URL hashing for security."""
        config = LinkTrackingConfig(
            tracking_domain="https://track.example.com", hash_urls=True
        )
        tracker = LinkTracker(config)

        html = '<a href="https://example.com/sensitive/path">Link</a>'

        result = tracker.track_links(html)

        assert "https://track.example.com/track/" in result
        assert "sensitive/path" not in result
        # Should contain a hash instead
        assert len(tracker.tracked_links[0].tracked_url.split("/")[-1]) == 16

    def test_dynamic_utm_content(self):
        """Test dynamic UTM content generation."""
        utm_params = UTMParams(
            utm_source="email",
            utm_medium="newsletter",
            utm_campaign="test",
            utm_content=None,  # Will be generated dynamically
        )

        html = """
        <a href="https://example.com" class="button">CTA Button</a>
        <h2><a href="https://example.com/blog">Blog Link</a></h2>
        <a href="https://example.com/shop">Buy Now</a>
        """

        self.tracker.track_links(html, utm_params)

        # Check that different content IDs were generated
        tracked_urls = [link.tracked_url for link in self.tracker.tracked_links]
        assert any("utm_content=cta_button" in url for url in tracked_urls)
        assert any("utm_content=header_h2" in url for url in tracked_urls)
        assert any("utm_content=shop_link" in url for url in tracked_urls)

    def test_tracking_report(self):
        """Test tracking report generation."""
        utm_params = UTMParams(
            utm_source="email", utm_medium="newsletter", utm_campaign="test"
        )

        html = """
        <a href="https://example.com">Home</a>
        <a href="https://example.com/about">About</a>
        """

        self.tracker.track_links(html, utm_params)
        report = self.tracker.get_tracking_report()

        assert report["total_links"] == 2
        assert len(report["tracked_links"]) == 2
        assert report["tracking_config"]["utm_params"]["utm_source"] == "email"

    def test_link_map_creation(self):
        """Test link ID to URL mapping."""
        html = """
        <a href="https://example.com">Home</a>
        <a href="https://example.com/products">Products</a>
        """

        self.tracker.track_links(html)
        link_map = self.tracker.create_link_map()

        assert len(link_map) == 2
        # Check that IDs map to original URLs
        for link_id, url in link_map.items():
            assert url in ["https://example.com", "https://example.com/products"]

    def test_empty_html(self):
        """Test handling of empty HTML."""
        result = self.tracker.track_links("")
        assert result == ""
        assert len(self.tracker.tracked_links) == 0

    def test_no_links(self):
        """Test HTML without links."""
        html = "<p>No links here</p>"
        result = self.tracker.track_links(html)
        assert result == html
        assert len(self.tracker.tracked_links) == 0

    def test_tracked_link_metadata(self):
        """Test tracked link metadata collection."""
        html = """
        <div class="footer">
            <a href="https://example.com">Visit our website</a>
        </div>
        """

        self.tracker.track_links(html)

        tracked_link = self.tracker.tracked_links[0]
        assert tracked_link.link_text == "Visit our website"
        assert "footer" in tracked_link.element_context
        assert tracked_link.original_url == "https://example.com"
