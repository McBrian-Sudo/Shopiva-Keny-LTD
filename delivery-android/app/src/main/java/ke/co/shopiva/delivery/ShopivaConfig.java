package ke.co.shopiva.delivery;

public final class ShopivaConfig {
    private ShopivaConfig() {}

    // Production Shopiva service.
    public static final String BASE_URL = "https://shopiva-keny-ltd.onrender.com";
    public static final String LOCATION_ENDPOINT = BASE_URL + "/delivery/location/ping/";
    public static final long UPDATE_INTERVAL_MS = 20_000L;
    public static final long FASTEST_INTERVAL_MS = 10_000L;
}
