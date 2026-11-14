# SDK 1.0.0-dev.2 compatibility backport

Base: b396484e5399d59f430bdde31c0a77e167f6acf2.
Includes the complete upstream Unicode-path fix from PR #226 (f45dfac2d8fcdccd72c911798140c2e7fbeb592b), without later API changes beyond dev.2.

Targeted validation: descriptor_import_request_cache_test and plugin_catalog_test passed.

Also includes upstream PR #241 (3367f2ee2b2cf6bfe4812a927dfe7861e37d1082): MaterializedSeriesView::nullCount() and isNull() expose Arrow validity bits. This is a client-side helper addition, without changing host ABI or feature floors; the unrelated #239 breaking API changes are not included.
