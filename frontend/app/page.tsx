"use client";

import { useState, useRef } from "react";
import {
  analyzeBody,
  analyzeSkin,
  getRecommendation,
  BodyAnalysisResult,
  SkinToneResult,
  FullRecommendationResponse,
} from "@/lib/api";

type Step = "upload" | "analyzing" | "results" | "error";

const OCCASIONS = ["casual", "formal", "ethnic", "party", "sport"];

export default function Home() {
  const [step, setStep] = useState<Step>("upload");
  const [bodyFile, setBodyFile] = useState<File | null>(null);
  const [bodyPreview, setBodyPreview] = useState<string | null>(null);
  const [faceFile, setFaceFile] = useState<File | null>(null);
  const [facePreview, setFacePreview] = useState<string | null>(null);
  const [occasion, setOccasion] = useState("casual");
  const [heightCm, setHeightCm] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const [bodyResult, setBodyResult] = useState<BodyAnalysisResult | null>(null);
  const [skinResult, setSkinResult] = useState<SkinToneResult | null>(null);
  const [recommendation, setRecommendation] = useState<FullRecommendationResponse | null>(null);

  const bodyInputRef = useRef<HTMLInputElement>(null);
  const faceInputRef = useRef<HTMLInputElement>(null);

  const dossierCode = `SF-${new Date().getFullYear()} · ${String(Math.floor(Math.random() * 900) + 100)}`;

  function handleFileSelect(
    e: React.ChangeEvent<HTMLInputElement>,
    setFile: (f: File) => void,
    setPreview: (s: string) => void
  ) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFile(file);
    setPreview(URL.createObjectURL(file));
  }

  async function runAnalysis() {
    if (!bodyFile || !faceFile) {
      setErrorMsg("Please upload both a full-body photo and a face photo.");
      return;
    }
    setStep("analyzing");
    setErrorMsg("");
    try {
      const [body, skin] = await Promise.all([
        analyzeBody(bodyFile, heightCm ? Number(heightCm) : undefined),
        analyzeSkin(faceFile),
      ]);
      setBodyResult(body);
      setSkinResult(skin);

      const rec = await getRecommendation({
        body_shape: body.body_shape,
        undertone: skin.undertone,
        skin_shade_group: skin.skin_shade_group,
        occasion,
      });
      setRecommendation(rec);
      setStep("results");
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Something went wrong during analysis. Please try clearer photos.";
      setErrorMsg(detail);
      setStep("error");
    }
  }

  function reset() {
    setStep("upload");
    setBodyFile(null);
    setBodyPreview(null);
    setFaceFile(null);
    setFacePreview(null);
    setBodyResult(null);
    setSkinResult(null);
    setRecommendation(null);
    setErrorMsg("");
  }

  return (
    <main className="min-h-screen bg-paper text-ink">
      {/* Masthead */}
      <header className="border-b hairline border-line px-6 py-5 flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <h1 className="font-display text-2xl tracking-tight">SmartFit AI Pro X</h1>
          <span className="font-mono text-xs text-muted uppercase tracking-wider">Style Dossier</span>
        </div>
        <span className="font-mono text-xs text-muted hidden sm:block">Vol. 01 — Body &amp; Color Intelligence</span>
      </header>

      <div className="max-w-3xl mx-auto px-6 py-12">
        {step === "upload" && (
          <section>
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-2">01 · Submission</p>
            <h2 className="font-display text-3xl mb-6 leading-snug">
              Upload two photos to open your dossier.
            </h2>

            <div className="grid sm:grid-cols-2 gap-6 mb-8">
              <UploadSlot
                label="Full-body photo"
                hint="Front-facing, good lighting, plain background works best."
                preview={bodyPreview}
                onClick={() => bodyInputRef.current?.click()}
              />
              <input
                ref={bodyInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFileSelect(e, setBodyFile, setBodyPreview)}
              />

              <UploadSlot
                label="Face close-up photo"
                hint="Natural light, no filters, for accurate skin tone reading."
                preview={facePreview}
                onClick={() => faceInputRef.current?.click()}
              />
              <input
                ref={faceInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => handleFileSelect(e, setFaceFile, setFacePreview)}
              />
            </div>

            <div className="grid sm:grid-cols-2 gap-6 mb-8">
              <div>
                <label className="font-mono text-xs text-muted uppercase tracking-widest block mb-2">
                  Height in cm (optional)
                </label>
                <input
                  type="number"
                  value={heightCm}
                  onChange={(e) => setHeightCm(e.target.value)}
                  placeholder="e.g. 172"
                  className="w-full border hairline border-line bg-transparent px-3 py-2 font-mono text-sm focus:outline-none"
                />
              </div>
              <div>
                <label className="font-mono text-xs text-muted uppercase tracking-widest block mb-2">
                  Occasion
                </label>
                <select
                  value={occasion}
                  onChange={(e) => setOccasion(e.target.value)}
                  className="w-full border hairline border-line bg-transparent px-3 py-2 font-mono text-sm focus:outline-none capitalize"
                >
                  {OCCASIONS.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
              </div>
            </div>

            {errorMsg && (
              <p className="text-sm text-red-700 mb-4 font-mono">{errorMsg}</p>
            )}

            <button
              onClick={runAnalysis}
              className="bg-signal text-paper font-mono text-sm uppercase tracking-widest px-6 py-3 hover:opacity-90 transition-opacity"
            >
              Open my dossier →
            </button>
          </section>
        )}

        {step === "analyzing" && (
          <section className="py-24 text-center">
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-3">Processing</p>
            <h2 className="font-display text-2xl">Reading proportions and pigment…</h2>
          </section>
        )}

        {step === "error" && (
          <section className="py-16">
            <p className="font-mono text-xs text-red-700 uppercase tracking-widest mb-3">Could not complete analysis</p>
            <p className="mb-6">{errorMsg}</p>
            <button onClick={reset} className="font-mono text-sm underline">Start over</button>
          </section>
        )}

        {step === "results" && bodyResult && skinResult && recommendation && (
          <section>
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-2">{dossierCode}</p>
            <h2 className="font-display text-3xl mb-1">Your Style Dossier</h2>
            <p className="text-muted mb-10">Fashion Score: <span className="font-mono text-ink">{recommendation.fashion_score}/100</span></p>

            {/* Body + Skin summary chips */}
            <div className="grid sm:grid-cols-2 gap-6 mb-10">
              <div className="border hairline border-line p-5">
                <p className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Body Shape</p>
                <p className="font-display text-2xl mb-2">{bodyResult.body_shape}</p>
                <p className="text-sm text-muted">{Math.round(bodyResult.confidence * 100)}% confidence</p>
              </div>
              <div className="border hairline border-line p-5">
                <p className="font-mono text-xs text-muted uppercase tracking-widest mb-2">Undertone</p>
                <div className="flex items-center gap-3 mb-2">
                  <span
                    className="w-6 h-6 rounded-full border border-line inline-block"
                    style={{ backgroundColor: skinResult.hex_color }}
                  />
                  <p className="font-display text-2xl">{skinResult.undertone}</p>
                </div>
                <p className="text-sm text-muted">{skinResult.skin_shade_group} shade group</p>
              </div>
            </div>

            {/* Pantone-style swatch dossier — signature element */}
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-3">02 · Your Palette</p>
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-3 mb-3">
              {recommendation.color_recommendation.palette_hex.map((hex, i) => (
                <div key={hex} className="border hairline border-line">
                  <div className="h-20" style={{ backgroundColor: hex }} />
                  <div className="px-2 py-1.5">
                    <p className="font-mono text-[10px] text-muted">{dossierCode.split(" ")[0]}-{String(i + 1).padStart(2, "0")}</p>
                    <p className="font-mono text-[10px] uppercase">{hex}</p>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-sm text-muted mb-10">{recommendation.color_recommendation.reasoning}</p>

            {/* Style summary */}
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-3">03 · Reading</p>
            <p className="font-display text-xl leading-relaxed mb-10">{recommendation.style_summary}</p>

            {/* Clothing recommendations */}
            <p className="font-mono text-xs text-muted uppercase tracking-widest mb-3">04 · Recommendations</p>
            <div className="divide-y hairline divide-line border-t border-b hairline border-line mb-10">
              {recommendation.clothing_recommendations.map((rec) => (
                <div key={rec.category} className="py-4 grid sm:grid-cols-3 gap-2">
                  <p className="font-mono text-xs uppercase tracking-widest text-muted">{rec.category}</p>
                  <p className="sm:col-span-2">
                    <span className="font-medium">{rec.items.join(", ")}</span>
                    <span className="block text-sm text-muted mt-1">{rec.reasoning}</span>
                  </p>
                </div>
              ))}
            </div>

            <div className="flex gap-4">
              <button onClick={reset} className="font-mono text-sm underline">
                Run a new analysis
              </button>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

function UploadSlot({
  label,
  hint,
  preview,
  onClick,
}: {
  label: string;
  hint: string;
  preview: string | null;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      type="button"
      className="border hairline border-line p-4 text-left hover:bg-black/[0.02] transition-colors"
    >
      {preview ? (
        <img src={preview} alt={label} className="w-full h-40 object-cover mb-3" />
      ) : (
        <div className="w-full h-40 mb-3 flex items-center justify-center border hairline border-dashed border-line">
          <span className="font-mono text-xs text-muted">Tap to upload</span>
        </div>
      )}
      <p className="font-mono text-xs uppercase tracking-widest mb-1">{label}</p>
      <p className="text-xs text-muted">{hint}</p>
    </button>
  );
}
