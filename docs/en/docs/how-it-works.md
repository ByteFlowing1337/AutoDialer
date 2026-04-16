# How It Works

## Execution Flow

AutoDialer follows a small, predictable flow:

1. Resolve the default gateway IP for the current operating system.
2. Send an HTTP request to the router homepage and infer the vendor from response fingerprints.
3. Load the matching router API class from `src/autodialer/routers/`.
4. Query the current WAN protocol.
5. Run the protocol-specific action.
6. Verify the resulting IP/ASN string with online APIs.

The CLI entry point for reconnection lives in `src/autodialer/reconnection.py`, and the device listing entry point lives in `src/autodialer/get_devices.py`.

## Gateway Detection

Gateway detection is implemented in `src/autodialer/utils/get_gateway.py`.

- Windows uses `route print -4`.
- Linux reads `/proc/net/route` first, then falls back to `ip -4 route show default`.
- macOS or BSD use `route -n get default`, then fall back to `netstat -rn`.

The helper also normalizes IPv4 and IPv6 addresses so they can be used safely in router URLs.

## Vendor Detection

Vendor detection is implemented in `src/autodialer/utils/check_vendor.py`.

The current logic:

- requests `http://<gateway>`,
- checks the HTML `<title>` when present,
- falls back to redirect URLs and `Location` headers,
- scans response headers and the HTML body for known vendor markers, and
- returns the first matching vendor name.

The registry lookup in `src/autodialer/utils/get_vendor_api.py` then discovers router implementations dynamically by scanning `*_api.py` files and reading each class's `SUPPORTED_VENDORS`.

## Reconnection Modes

### `--force`

`autodialer --force` reconnects once, then checks the ISP/org string and logs the result if the check succeeds.

### `--asn <ASN>`

`autodialer --asn <ASN>` first checks whether the current ISP already matches the requested ASN. If it does, the process exits successfully immediately. If not, AutoDialer reconnects and retries the ISP check until either:

- the target ASN is reached, or
- 5 reconnection attempts have been exhausted.

### `--change`
`autodialer --change` changes your IP address, if you are on the dynamic line.

## Router Support Status

The repository currently contains these router API modules:

| Router module | Status | Notes |
| :--- | :--- | :--- |
| `asus/asus_api.py` | Implemented | Used for `ASUS` and `ASUS AiMesh` fingerprints. |
| `tplink/tplink_api.py` | Implemented | Handles PPPoE, DHCP, and device listing. |
| `zte/zte_api.py` | Implemented | Handles PPPoE, DHCP, and device listing. |

Support is best understood as "implemented against known request/response shapes," not as a guarantee for every firmware revision from a vendor.

## Extending AutoDialer

To add a new router integration:

1. Create a new `*_api.py` module under `src/autodialer/routers/`.
2. Add a class with a `SUPPORTED_VENDORS` attribute.
3. Implement the methods expected by `RouterAPI` in `src/autodialer/routers/base_api.py`.
4. Add or update vendor fingerprints in `src/autodialer/utils/check_vendor.py`.
5. Add unit tests for the new behavior under `tests/`.

Because router APIs are vendor- and firmware-specific, keep request payloads isolated to the router module and prefer tests that mock network calls rather than reaching real devices.
