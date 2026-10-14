# Public endpoint contract

The firmware sends an HTTPS GET request to the configured public endpoint. The
response must be a JSON object containing a `points` array ordered from oldest
to newest.

Each usable item contains:

- `id` — a stable anonymous identifier used only to retain the point's position.
- `code` — `D`, `G`, or `C`, mapped locally to the three display colours.

The firmware intentionally ignores any colour value supplied by the server and
uses its local colour mapping. At most the final sixteen valid items are shown.

Do not expose participant names, contact details, precise location, text,
images, or other identifiable information through this endpoint.

