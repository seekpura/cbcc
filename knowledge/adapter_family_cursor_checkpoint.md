# Adapter Families / Cursor / Checkpoint

Marketplace, search and review feeds often arrive as pages or incremental exports. The runtime should preserve adapter family, cursor field, previous/next cursor, change set and declared completion hints while keeping coverage claims conservative. A high-watermark or `has_more=false` is only as authoritative as the host/source contract.
