"use client";

import { useState, type FormEvent } from "react";

import {
  previewDigest as requestPreview,
  sendDigest as requestSend,
  type DigestLimits,
  type DigestPreviewResponse,
  type DigestSources,
  type LimitedSourceKey,
  type SourceKey,
} from "@/lib/api";

const SOURCE_OPTIONS: {
  key: SourceKey;
  name: string;
  description: string;
}[] = [
  {
    key: "hn",
    name: "Hacker News",
    description: "Popular AI engineering and startup discussions",
  },
  {
    key: "techcrunch",
    name: "TechCrunch",
    description: "AI company, product, and industry news",
  },
  {
    key: "arxiv",
    name: "arXiv",
    description: "Recent AI and machine learning research papers",
  },
  {
    key: "tip",
    name: "AI Engineering Tip",
    description: "A practical tip included at the end of the digest",
  },
];

const DEFAULT_SOURCES: DigestSources = {
  hn: true,
  techcrunch: true,
  arxiv: true,
  tip: true,
};

const DEFAULT_LIMITS: DigestLimits = {
  hn: 3,
  techcrunch: 3,
  arxiv: 3,
};

type ActiveRequest = "preview" | "send" | null;

export default function Home() {
  const [sources, setSources] = useState<DigestSources>(DEFAULT_SOURCES);
  const [limits, setLimits] = useState<DigestLimits>(DEFAULT_LIMITS);
  const [recipient, setRecipient] = useState("");
  const [preview, setPreview] = useState<DigestPreviewResponse | null>(null);
  const [activeRequest, setActiveRequest] = useState<ActiveRequest>(null);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const isLoading = activeRequest !== null;

  function clearMessages() {
    setSuccessMessage("");
    setErrorMessage("");
  }

  function validateSources(): boolean {
    if (Object.values(sources).some(Boolean)) {
      return true;
    }

    setErrorMessage("Select at least one digest source.");
    return false;
  }

  function toggleSource(key: SourceKey) {
    setSources((current) => ({
      ...current,
      [key]: !current[key],
    }));
    clearMessages();
  }

  function updateLimit(key: LimitedSourceKey, value: number) {
    const safeValue = Math.min(Math.max(value, 1), 20);

    setLimits((current) => ({
      ...current,
      [key]: safeValue,
    }));
    clearMessages();
  }

  async function handlePreview() {
    clearMessages();

    if (!validateSources()) {
      return;
    }

    setActiveRequest("preview");

    try {
      const response = await requestPreview({ sources, limits });
      setPreview(response);
      setSuccessMessage("Digest preview generated successfully.");
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to generate preview.",
      );
    } finally {
      setActiveRequest(null);
    }
  }

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearMessages();

    if (!validateSources()) {
      return;
    }

    if (!recipient.trim()) {
      setErrorMessage("Enter a recipient email address.");
      return;
    }

    setActiveRequest("send");

    try {
      const response = await requestSend({
        recipient: recipient.trim(),
        sources,
        limits,
      });

      setSuccessMessage(response.message);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Unable to send digest.",
      );
    } finally {
      setActiveRequest(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600">
            AI Daily Digest
          </p>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Build your daily AI briefing
          </h1>
          <p className="mt-3 max-w-2xl text-slate-600">
            Choose your sources, preview the generated digest, and send it
            directly to your inbox.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
          <form
            onSubmit={handleSend}
            className="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <section>
              <h2 className="text-lg font-semibold">Digest sources</h2>
              <p className="mt-1 text-sm text-slate-500">
                Select the content you want to include.
              </p>

              <div className="mt-5 space-y-3">
                {SOURCE_OPTIONS.map((option) => {
                  return (
                    <div
                      key={option.key}
                      className="rounded-xl border border-slate-200 p-4"
                    >
                      <div className="flex items-start gap-3">
                        <input
                          id={option.key}
                          type="checkbox"
                          checked={sources[option.key]}
                          onChange={() => toggleSource(option.key)}
                          disabled={isLoading}
                          className="mt-1 h-4 w-4 accent-indigo-600"
                        />

                        <div className="min-w-0 flex-1">
                          <label
                            htmlFor={option.key}
                            className="cursor-pointer font-medium"
                          >
                            {option.name}
                          </label>
                          <p className="mt-1 text-sm text-slate-500">
                            {option.description}
                          </p>
                        </div>

                        {option.key !== "tip" && (
                          <div className="ml-2">
                            <label
                              htmlFor={`${option.key}-limit`}
                              className="block text-xs font-medium text-slate-500"
                            >
                              Items
                            </label>
                            <input
                              id={`${option.key}-limit`}
                              type="number"
                              min="1"
                              max="20"
                              value={limits[option.key]}
                              disabled={!sources[option.key] || isLoading}
                              onChange={(event) =>
                                updateLimit(
                                  option.key as LimitedSourceKey,
                                  Number(event.target.value),
                                )
                              }
                              className="mt-1 w-16 rounded-lg border border-slate-300 px-2 py-1.5 text-center disabled:bg-slate-100 disabled:text-slate-400"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="mt-7">
              <label htmlFor="recipient" className="text-lg font-semibold">
                Recipient email
              </label>
              <p className="mt-1 text-sm text-slate-500">
                Required only when sending the digest.
              </p>
              <input
                id="recipient"
                type="email"
                value={recipient}
                onChange={(event) => {
                  setRecipient(event.target.value);
                  clearMessages();
                }}
                disabled={isLoading}
                placeholder="you@example.com"
                className="mt-4 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              />
            </section>

            {errorMessage && (
              <div
                role="alert"
                className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
              >
                {errorMessage}
              </div>
            )}

            {successMessage && (
              <div
                role="status"
                className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
              >
                {successMessage}
              </div>
            )}

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={handlePreview}
                disabled={isLoading}
                className="rounded-xl border border-indigo-600 px-4 py-3 font-semibold text-indigo-600 transition hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {activeRequest === "preview"
                  ? "Generating..."
                  : "Preview Digest"}
              </button>

              <button
                type="submit"
                disabled={isLoading}
                className="rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {activeRequest === "send" ? "Sending..." : "Send Digest"}
              </button>
            </div>
          </form>

          <section className="min-h-[600px] rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold">Digest preview</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Preview the email before sending it.
                </p>
              </div>

              {preview && (
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    preview.mock
                      ? "bg-amber-100 text-amber-700"
                      : "bg-emerald-100 text-emerald-700"
                  }`}
                >
                  {preview.mock ? "Mock data" : "Live data"}
                </span>
              )}
            </div>

            {!preview ? (
              <div className="flex min-h-[500px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 text-center">
                <div>
                  <p className="font-medium text-slate-700">
                    No preview generated yet
                  </p>
                  <p className="mt-2 text-sm text-slate-500">
                    Choose your sources and click Preview Digest.
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <p className="mb-4 rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
                  {preview.message}
                </p>

                {preview.warnings && preview.warnings.length > 0 && (
                  <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                    <p className="font-semibold">Source warnings</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {preview.warnings.map((warning) => (
                        <li key={warning}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <iframe
                  title="AI Daily Digest email preview"
                  srcDoc={preview.html}
                  sandbox=""
                  className="h-[650px] w-full rounded-xl border border-slate-200 bg-white"
                />
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}