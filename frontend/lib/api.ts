export type SourceKey = "hn" | "techcrunch" | "arxiv" | "tip";
export type LimitedSourceKey = Exclude<SourceKey, "tip">;

export type DigestSources = Record<SourceKey, boolean>;
export type DigestLimits = Record<LimitedSourceKey, number>;

export interface DigestPreviewItem {
  source: string;
  title: string;
  url: string;
  score: number | null;
}

export interface DigestPreviewRequest {
  sources: DigestSources;
  limits: DigestLimits;
}

export interface DigestPreviewResponse {
  mock: boolean;
  message: string;
  items: DigestPreviewItem[];
  sources: DigestSources;
  tip: string | null;
  warnings: string[] | null;
  html: string;
}

export interface DigestSendRequest extends DigestPreviewRequest {
  recipient: string;
}

export interface DigestSendResponse {
  sent: boolean;
  message: string;
  warnings: string[] | null;
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function postJson<ResponseType>(
  path: string,
  body: object,
): Promise<ResponseType> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data: unknown = await response.json();

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    if (
      typeof data === "object" &&
      data !== null &&
      "detail" in data &&
      typeof data.detail === "string"
    ) {
      message = data.detail;
    }

    throw new Error(message);
  }

  return data as ResponseType;
}

export function previewDigest(
  request: DigestPreviewRequest,
): Promise<DigestPreviewResponse> {
  return postJson<DigestPreviewResponse>("/api/digest/preview", request);
}

export function sendDigest(
  request: DigestSendRequest,
): Promise<DigestSendResponse> {
  return postJson<DigestSendResponse>("/api/digest/send", request);
}