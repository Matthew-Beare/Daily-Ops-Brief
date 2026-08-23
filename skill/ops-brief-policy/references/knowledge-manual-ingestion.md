# Knowledge and Product-Manual Ingestion

Load this reference when the user supplies a product manual, service manual, datasheet, warranty guide, technical PDF, download URL, uploaded file, email attachment, or other durable reference that should remain queryable in LifeOS.

## Interim authority

Until the self-hosted LifeOS database/object store is deployed:

- keep the original manual/reference file in the canonical Google Drive `Manuals & Reference` hierarchy;
- index searchable metadata and relationships in the canonical `Knowledge Index` Sheet;
- treat Drive as the evidence/file store and the Sheet as the searchable index, not chat history;
- preserve identifiers so a later PostgreSQL/object-store migration can retain the same Knowledge UUID and asset relationships.

A chat, upload, email, URL, and Drive copy may be multiple evidence paths to one reference. Do not create duplicate knowledge records merely because the same manual arrives twice.

## Identity and dedupe

Every canonical knowledge object gets one immutable RFC 4122 UUID (`Entity UUID`). Never recycle or mutate that UUID when a title, filename, folder, manufacturer, model, tags, or related asset changes. A readable `Knowledge ID` is an alias for humans, not the primary identity.

Before creating a record, search existing knowledge by:

1. exact Drive file ID or content hash when available;
2. source URL plus revision/version;
3. manufacturer + model/part number + document type/version;
4. normalized title/filename plus related asset when uniquely identifying.

If existing evidence identifies the same manual, enrich/update that record and preserve the UUID.

## Intake and filing

1. Inspect the supplied file/link and determine document type, manufacturer/publisher, title, model/part/SKU, revision/version, effective/publication date, language, and related asset(s) when supported.
2. Prefer the manufacturer's/OEM's official download/source when available. Preserve the original supplied source URL as provenance even when a stronger canonical source is found.
3. Save or copy the retained file into the canonical Drive `Manuals & Reference` hierarchy using a readable filename. Never place credentials or secrets in filenames/metadata.
4. Link the file to existing asset UUID(s), receipt IDs, part numbers, or projects when evidence supports the relationship. Do not create a duplicate asset merely because a manual exists.
5. Upsert one `Knowledge Index` row containing Knowledge ID, Entity UUID, title/type, manufacturer/model/part, related asset UUID/ID, source URL, Drive file URL/ID, version/date, tags, concise summary, status, and update timestamp.
6. Verify the Drive file and Sheet row by readback before claiming ingestion complete.

## Search and answer behavior

When the user later asks for a manual, procedure, specification, torque value, setup instruction, or similar reference:

- search the Knowledge Index by asset UUID/ID, manufacturer, model, part/SKU, title, tags, and aliases;
- read the relevant source content when needed rather than answering only from remembered chat context;
- answer with the evidence-backed result and surface the canonical Drive link to the manual/reference;
- cite page/section/revision when the source supports it;
- distinguish source facts from inference.

Preserve relevant extracted facts/provenance in the knowledge system when useful, but do not duplicate an entire copyrighted manual into Git or Sheet cells. The retained Drive file remains the canonical document.

## Asset acquisition interaction

A manual can enrich an existing asset with verified model/specification/warranty/application information, but asset identity remains governed by `asset-acquisition.md`. If the manual proves a previously ambiguous part/asset relationship, update that relationship using the existing immutable asset UUID rather than creating another physical asset.

## Completion gate

Manual/reference ingestion is complete only after dedupe, durable Drive filing, Knowledge UUID assignment, metadata/asset linkage, index upsert, and readback all succeed. If the file cannot be downloaded or Drive is unavailable, surface a precise Action Required instead of leaving the only copy in chat.