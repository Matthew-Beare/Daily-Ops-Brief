"use strict";

(() => {
  const TABLE = "ReceiptProcessing";
  const HEADERS = [
    "receipt_uuid", "evidence_uuid", "evidence_sha256", "stage", "status", "source_kind",
    "extracted_text_sha256", "parser_version", "attempts", "next_attempt_at", "last_error",
    "claimed_by", "claimed_at", "created_at", "updated_at", "completed_at"
  ];
  const callbacks = new Map();
  let sequence = 0;
  let ensuredForWorkbook = "";
  const previousCallback = globalThis.onMirrorNativeGoogleApiResponse;

  function now() { return new Date().toISOString(); }
  function nativeReady() { return Boolean(globalThis.MirrorNative?.googleApiRequest); }
  function authority() { return globalThis.MiraGoogleAuthority?.authority?.() || null; }
  function encodeRange(value) { return encodeURIComponent(value).replace(/%2F/g, "/"); }

  function request(method, url, body = "", contentType = "application/json; charset=utf-8") {
    if (!nativeReady()) return Promise.reject(new Error("This build has no Google MIRROR transport."));
    const requestId = `receipt-queue-${Date.now()}-${++sequence}`;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        callbacks.delete(requestId);
        reject(new Error("Google did not answer the receipt queue request within two minutes."));
      }, 120000);
      callbacks.set(requestId, { resolve, reject, timer });
      try { globalThis.MirrorNative.googleApiRequest(requestId, method, url, body, contentType); }
      catch (error) { clearTimeout(timer); callbacks.delete(requestId); reject(error); }
    });
  }

  globalThis.onMirrorNativeGoogleApiResponse = function receiptQueueGoogleResponse(requestId, status, responseText) {
    const pending = callbacks.get(requestId);
    if (!pending) {
      if (typeof previousCallback === "function") previousCallback(requestId, status, responseText);
      return;
    }
    callbacks.delete(requestId);
    clearTimeout(pending.timer);
    const code = Number(status);
    let json = {};
    try { json = responseText ? JSON.parse(String(responseText)) : {}; } catch (_) { json = {}; }
    if (code < 200 || code >= 300) {
      const detail = json?.error?.message || json?.error || responseText || `Google returned HTTP ${code}.`;
      pending.reject(new Error(typeof detail === "string" ? detail : JSON.stringify(detail)));
      return;
    }
    pending.resolve({ status: code, json, text: String(responseText || "") });
  };

  async function ensureTable() {
    if (!globalThis.MiraGoogleAuthority?.ready) throw new Error("Google MIRROR is not available in this build.");
    if (!(await globalThis.MiraGoogleAuthority.ready())) throw new Error("Connect Google before queueing receipt processing.");
    const info = authority();
    if (!info?.workbook_id) throw new Error("MIRROR workbook is not connected.");
    if (ensuredForWorkbook === info.workbook_id) return info;

    const workbookUrl = `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}?fields=sheets.properties`;
    const workbook = (await request("GET", workbookUrl)).json;
    const exists = (workbook.sheets || []).some((sheet) => sheet.properties?.title === TABLE);
    if (!exists) {
      await request(
        "POST",
        `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}:batchUpdate`,
        JSON.stringify({ requests: [{ addSheet: { properties: { title: TABLE } } }] })
      );
    }
    const headerRange = encodeRange(`'${TABLE}'!A1:P1`);
    await request(
      "PUT",
      `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${headerRange}?valueInputOption=RAW`,
      JSON.stringify({ range: `'${TABLE}'!A1:P1`, majorDimension: "ROWS", values: [HEADERS] })
    );

    // Upgrade the user-owned authority manifest after the additive queue table exists.
    if (info.manifest_file_id) {
      const manifest = {
        schema_version: 4,
        authority_uuid: info.authority_uuid,
        authority_name: info.authority_name || "MIRA MIRROR Reality Record",
        workbook_file_id: info.workbook_id,
        folder_id: info.folder_id || "",
        created_at: info.created_at || now(),
        upgraded_at: now(),
        product: "MIRA",
        data_layer: "MIRROR"
      };
      await request(
        "PATCH",
        `https://www.googleapis.com/upload/drive/v3/files/${encodeURIComponent(info.manifest_file_id)}?uploadType=media`,
        JSON.stringify(manifest)
      );
      await request(
        "PATCH",
        `https://www.googleapis.com/drive/v3/files/${encodeURIComponent(info.manifest_file_id)}?fields=id,appProperties`,
        JSON.stringify({ appProperties: { mira_mirror: "authority_manifest", schema_version: "4", authority_uuid: info.authority_uuid, workbook_id: info.workbook_id } })
      );
    }
    ensuredForWorkbook = info.workbook_id;
    return info;
  }

  async function rows() {
    const info = await ensureTable();
    const range = encodeRange(`'${TABLE}'!A:P`);
    const result = (await request(
      "GET",
      `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${range}?majorDimension=ROWS`
    )).json;
    const values = result.values || [];
    const headers = values[0] || HEADERS;
    return values.slice(1).map((row) => Object.fromEntries(headers.map((key, index) => [key, row[index] ?? ""])));
  }

  async function queueReceipt(receipt) {
    if (!receipt?.receipt_uuid) throw new Error("MIRROR did not return a receipt identity.");
    const info = await ensureTable();
    const existing = (await rows()).find((row) => row.receipt_uuid === receipt.receipt_uuid);
    if (existing) return { processing: existing, readback_verified: true };

    const evidence = (await globalThis.MiraGoogleAuthority.tableValues("Evidence")).objects.find(
      (row) => row.receipt_uuid === receipt.receipt_uuid
    );
    const timestamp = now();
    const row = [
      receipt.receipt_uuid,
      evidence?.evidence_uuid || "",
      evidence?.sha256 || "",
      "captured",
      "queued",
      evidence?.mime_type?.startsWith("image/") ? "image" : evidence?.mime_type === "application/pdf" ? "pdf" : "file",
      "", "", "0", "", "", "", "", timestamp, timestamp, ""
    ];
    const appendRange = encodeRange(`'${TABLE}'!A:P`);
    await request(
      "POST",
      `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(info.workbook_id)}/values/${appendRange}:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS`,
      JSON.stringify({ majorDimension: "ROWS", values: [row] })
    );
    const readback = (await rows()).find((item) => item.receipt_uuid === receipt.receipt_uuid);
    if (!readback || readback.status !== "queued" || readback.evidence_sha256 !== (evidence?.sha256 || "")) {
      throw new Error("Receipt was captured, but the MIRROR processing queue did not read back correctly.");
    }
    return { processing: readback, readback_verified: true };
  }

  document.addEventListener("mira:provider-state", (event) => {
    if (event.detail?.provider !== "google_workspace" || event.detail?.mirror_verified !== true) return;
    ensureTable().catch((error) => globalThis.MiraActionAudit?.announce?.(error?.message || String(error)));
  });

  globalThis.MiraReceiptQueue = { ensureTable, queueReceipt, rows };
})();
