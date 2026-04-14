const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { imageSizingContain, imageSizingCrop } = require("./pptxgenjs_helpers/image");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Bjorn Melin";
pptx.company = "UC Berkeley School of Information";
pptx.subject = "DS266 final project presentation";
pptx.title = "Can Reranking Make XSum More Factual?";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Liberation Sans",
  bodyFontFace: "Liberation Sans",
  lang: "en-US",
};

const COLORS = {
  berkeleyBlue: "003262",
  berkeleyBlueLight: "3B7EA1",
  gold: "FDB515",
  text: "243746",
  muted: "5F6B78",
  line: "D9E0E7",
  panel: "F7F9FB",
  white: "FFFFFF",
  success: "0B6E4F",
  warning: "B36A00",
};

const slidesDir = __dirname;
const figuresDir = path.resolve(__dirname, "../../../outputs/final/figures");
const assetsDir = path.resolve(__dirname, "./assets");
const outputPath = path.resolve(
  __dirname,
  "../../../outputs/final/submission/final_slides.pptx",
);
const logoPath = path.join(assetsDir, "berkeley_soi_logo.png");
const coverPath = path.join(assetsDir, "berkeley_cover.png");

function finalizeSlide(slide) {
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

function addNotes(slide, notes) {
  slide.addNotes(notes.trim());
}

function addFooter(slide, slideNumber) {
  slide.addImage({
    path: logoPath,
    ...imageSizingContain(logoPath, 0.42, 6.92, 1.75, 0.34),
  });
  slide.addText(String(slideNumber), {
    x: 12.35,
    y: 6.93,
    w: 0.45,
    h: 0.18,
    fontFace: "Liberation Sans",
    fontSize: 10,
    color: COLORS.muted,
    align: "right",
    margin: 0,
  });
}

function addContentFrame(slide, eyebrow, title, subtitle = "", slideNumber) {
  slide.background = { color: COLORS.white };
  slide.addText(eyebrow.toUpperCase(), {
    x: 0.68,
    y: 0.42,
    w: 2.6,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 11,
    bold: true,
    color: COLORS.berkeleyBlueLight,
    charSpace: 1.1,
    margin: 0,
  });
  slide.addText(title, {
    x: 0.68,
    y: 0.66,
    w: 11.6,
    h: 0.52,
    fontFace: "Liberation Sans",
    fontSize: 24,
    bold: true,
    color: COLORS.berkeleyBlue,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.68,
    y: 1.32,
    w: 11.85,
    h: 0,
    line: { color: COLORS.gold, width: 1.2 },
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.68,
      y: 1.4,
      w: 11.3,
      h: 0.34,
      fontFace: "Liberation Sans",
      fontSize: 13,
      color: COLORS.muted,
      italic: true,
      margin: 0,
    });
  }
  addFooter(slide, slideNumber);
}

function addBulletList(slide, items, opts) {
  const runs = [];
  items.forEach((item, index) => {
    runs.push({
      text: item,
      options: {
        breakLine: index !== items.length - 1,
        bullet: { indent: 16 },
      },
    });
  });
  slide.addText(runs, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    fontFace: "Liberation Sans",
    fontSize: opts.fontSize || 18,
    color: COLORS.text,
    breakLine: true,
    valign: "top",
    paraSpaceAfterPt: opts.paraSpaceAfterPt || 8,
    margin: 0,
  });
}

function addInfoCard(slide, label, body, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    rectRadius: 0.06,
    line: { color: opts.borderColor || COLORS.line, width: 1 },
    fill: { color: opts.fillColor || COLORS.panel },
  });
  slide.addText(label, {
    x: opts.x + 0.18,
    y: opts.y + 0.14,
    w: opts.w - 0.36,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 11,
    bold: true,
    color: opts.labelColor || COLORS.berkeleyBlueLight,
    margin: 0,
  });
  slide.addText(body, {
    x: opts.x + 0.18,
    y: opts.y + 0.36,
    w: opts.w - 0.36,
    h: opts.h - 0.5,
    fontFace: "Liberation Sans",
    fontSize: opts.fontSize || 15,
    bold: opts.bold || false,
    color: opts.bodyColor || COLORS.text,
    valign: "mid",
    margin: 0,
  });
}

function addMetricCard(slide, label, before, after, deltaLabel, opts = {}) {
  addInfoCard(slide, label, "", {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    fillColor: COLORS.white,
    borderColor: COLORS.line,
  });
  slide.addText(`${before} → ${after}`, {
    x: opts.x + 0.2,
    y: opts.y + 0.52,
    w: opts.w - 0.4,
    h: 0.44,
    fontFace: "Liberation Sans",
    fontSize: 23,
    bold: true,
    color: opts.valueColor || COLORS.berkeleyBlue,
    margin: 0,
  });
  slide.addText(deltaLabel, {
    x: opts.x + 0.2,
    y: opts.y + 1.06,
    w: opts.w - 0.4,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 11.5,
    color: opts.deltaColor || COLORS.muted,
    italic: true,
    margin: 0,
  });
}

function addNumberedTakeaway(slide, number, title, body, opts) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    rectRadius: 0.05,
    line: { color: COLORS.line, width: 1 },
    fill: { color: COLORS.panel },
  });
  slide.addShape(pptx.ShapeType.ellipse, {
    x: opts.x + 0.18,
    y: opts.y + 0.18,
    w: 0.42,
    h: 0.42,
    line: { color: COLORS.gold, width: 1 },
    fill: { color: COLORS.gold },
  });
  slide.addText(String(number), {
    x: opts.x + 0.18,
    y: opts.y + 0.205,
    w: 0.42,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 13,
    bold: true,
    color: COLORS.berkeleyBlue,
    align: "center",
    margin: 0,
  });
  slide.addText(title, {
    x: opts.x + 0.72,
    y: opts.y + 0.16,
    w: opts.w - 0.9,
    h: 0.24,
    fontFace: "Liberation Sans",
    fontSize: 15,
    bold: true,
    color: COLORS.berkeleyBlue,
    margin: 0,
  });
  slide.addText(body, {
    x: opts.x + 0.72,
    y: opts.y + 0.46,
    w: opts.w - 0.9,
    h: opts.h - 0.62,
    fontFace: "Liberation Sans",
    fontSize: 13.5,
    color: COLORS.text,
    margin: 0,
  });
}

function addDiagramNode(slide, label, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    rectRadius: 0.06,
    line: { color: COLORS.berkeleyBlue, width: opts.lineWidth || 1.6 },
    fill: { color: opts.fillColor || "E8F1FB" },
  });
  slide.addText(label, {
    x: opts.x + 0.14,
    y: opts.y + 0.18,
    w: opts.w - 0.28,
    h: opts.h - 0.28,
    fontFace: "Liberation Sans",
    fontSize: opts.fontSize || 14.5,
    bold: true,
    color: "1F2937",
    align: "center",
    valign: "mid",
    margin: 0,
  });
}

function addDiagramChip(slide, label, opts = {}) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    rectRadius: 0.05,
    line: { color: COLORS.berkeleyBlue, width: 1.4 },
    fill: { color: opts.fillColor || COLORS.white },
  });
  slide.addText(label, {
    x: opts.x + 0.08,
    y: opts.y + 0.11,
    w: opts.w - 0.16,
    h: opts.h - 0.16,
    fontFace: "Liberation Sans",
    fontSize: opts.fontSize || 11.5,
    bold: true,
    color: "1F2937",
    align: "center",
    valign: "mid",
    margin: 0,
  });
}

// Slide 1: title
{
  const slide = pptx.addSlide();
  slide.addImage({
    path: coverPath,
    ...imageSizingCrop(coverPath, 0, 0, 13.333, 7.5),
  });
  slide.addText("DS266 FINAL PROJECT", {
    x: 0.72,
    y: 0.72,
    w: 3.1,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 11,
    bold: true,
    color: COLORS.gold,
    charSpace: 1.4,
    margin: 0,
  });
  slide.addText("Reranking Improves\nFactuality on XSum", {
    x: 0.72,
    y: 1.0,
    w: 5.6,
    h: 1.35,
    fontFace: "Liberation Sans",
    fontSize: 28,
    bold: true,
    color: COLORS.white,
    margin: 0,
  });
  slide.addText("Factuality-aware reranking for extreme summarization", {
    x: 0.72,
    y: 2.52,
    w: 5.5,
    h: 0.3,
    fontFace: "Liberation Sans",
    fontSize: 15,
    color: COLORS.white,
    italic: true,
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.72,
    y: 2.98,
    w: 2.2,
    h: 0,
    line: { color: COLORS.gold, width: 1.6 },
  });
  slide.addText("Bounded study: fine-tuned BART, beam candidates, and post-generation reranking", {
    x: 0.72,
    y: 3.16,
    w: 6.15,
    h: 0.52,
    fontFace: "Liberation Sans",
    fontSize: 13.5,
    color: COLORS.white,
    margin: 0,
  });
  slide.addText("Bjorn Melin\nUC Berkeley School of Information\nApril 2026", {
    x: 0.72,
    y: 4.78,
    w: 3.9,
    h: 0.7,
    fontFace: "Liberation Sans",
    fontSize: 14,
    color: COLORS.white,
    margin: 0,
  });
  addNotes(
    slide,
    `
Timing: 0:30

Script:
This project asks a simple question: if I generate several summary candidates and then choose among them more carefully, can I make the final summary more factual? On this bounded XSum study, the answer was yes. I improved factuality meaningfully with reranking, while accepting a modest drop in ROUGE. The core pipeline was: fine-tune BART, generate beam candidates, score them with factuality signals, and then pick the best operating point.
    `,
  );
  finalizeSlide(slide);
}

// Slide 2: motivation and setup
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Context",
    "What this project is actually doing",
    "A few quick terms make the rest of the talk easier to follow.",
    2,
  );
  addBulletList(
    slide,
    [
      "Start with one article and generate several possible summaries instead of trusting only the single top-likelihood output.",
      "Score those candidates with factuality-oriented signals, then choose the best validation operating point.",
      "The goal is not a new model family; it is testing whether better selection improves groundedness.",
    ],
    { x: 0.78, y: 1.95, w: 4.9, h: 3.5, fontSize: 17.3, paraSpaceAfterPt: 8 },
  );
  addInfoCard(
    slide,
    "XSum",
    "Single-sentence news summarization benchmark with aggressive compression.",
    { x: 6.0, y: 1.92, w: 2.95, h: 1.28, fontSize: 13.5, fillColor: COLORS.white },
  );
  addInfoCard(
    slide,
    "Beam search",
    "A decoding method that keeps several likely next-word paths, giving multiple candidate summaries.",
    { x: 9.25, y: 1.92, w: 2.95, h: 1.46, fontSize: 12.9, fillColor: COLORS.white },
  );
  addInfoCard(
    slide,
    "Reranking",
    "Post-generation selection: choose among candidates using extra scores after decoding.",
    { x: 6.0, y: 3.66, w: 2.95, h: 1.48, fontSize: 13.2, fillColor: COLORS.panel },
  );
  addInfoCard(
    slide,
    "ROUGE",
    "An overlap metric: it rewards wording similarity to the reference summary, not factual correctness by itself.",
    { x: 9.25, y: 3.66, w: 2.95, h: 1.48, fontSize: 12.6, fillColor: COLORS.panel },
  );
  addInfoCard(
    slide,
    "Why this matters",
    "If reranking works, factual quality can improve without replacing the generator itself.",
    { x: 6.0, y: 5.46, w: 6.2, h: 0.88, fontSize: 13.2, fillColor: COLORS.white },
  );
  addNotes(
    slide,
    `
Timing: 0:35

Script:
Before the results, here are the few terms that matter. XSum is a news summarization benchmark where the target is a single very short summary sentence. Beam search just means the model generates several plausible summaries instead of only one. Reranking means I score those candidates again after generation and choose the one that looks best under my scoring rule. ROUGE is a wording-overlap metric with the reference summary, so it is useful, but it does not directly tell us whether the summary is actually true. The point of this project was not to invent a new model family. It was to test whether better selection improves groundedness.
    `,
  );
  finalizeSlide(slide);
}

// Slide 3: motivation and setup
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Problem",
    "Why fluent XSum summaries can still be wrong",
    "The goal was better factual support without hiding the overlap trade-off.",
    3,
  );
  addBulletList(
    slide,
    [
      "XSum rewards extreme compression, so fluent summaries can still insert unsupported entities or relations.",
      "ROUGE captures overlap, but not whether a claim is actually grounded in the source article.",
      "The baseline is the public BART XSum model, so the gain comes from selection rather than a different generator.",
    ],
    { x: 0.78, y: 1.95, w: 6.0, h: 3.55, fontSize: 17.8, paraSpaceAfterPt: 8 },
  );
  addInfoCard(
    slide,
    "Research question",
    "Can reranking trade a little ROUGE for meaningfully stronger factuality?",
    { x: 7.35, y: 1.92, w: 5.15, h: 1.24, fontSize: 15, bold: true, fillColor: COLORS.white },
  );
  addInfoCard(slide, "Baseline", "Public BART baseline\nbeam search only\nno factuality fusion", {
    x: 7.35,
    y: 3.34,
    w: 2.45,
    h: 1.45,
    fontSize: 14,
    fillColor: COLORS.panel,
  });
  addInfoCard(slide, "Scope", "train 128\nval 64 / 128\ntest 128\nqualitative 24", {
    x: 10.05,
    y: 3.34,
    w: 2.45,
    h: 1.45,
    fontSize: 14,
    fillColor: COLORS.panel,
    bold: true,
  });
  addInfoCard(
    slide,
    "Success criterion",
    "Higher factuality composite on the bounded test split, with the ROUGE cost reported rather than hidden.",
    { x: 7.35, y: 5.02, w: 5.15, h: 1.18, fontSize: 14, fillColor: COLORS.panel },
  );
  addNotes(
    slide,
    `
Timing: 0:50

Script:
XSum is a hard factuality setting because it rewards aggressive compression. The summaries are short and often very fluent, but that fluency can hide unsupported facts, wrong entities, or incorrect relations. My baseline here is the public BART XSum model using normal beam-search decoding. So the question is not whether a different generator wins. The question is whether reranking can trade a small amount of ROUGE for meaningfully stronger factuality. I treated success as a higher factuality composite on the bounded test split while reporting the ROUGE cost explicitly.
    `,
  );
  finalizeSlide(slide);
}

// Slide 4: method
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Method",
    "Generate candidates, score them, choose the operating point",
    "The method is intentionally simple: no new model family, just better candidate selection.",
    4,
  );
  addDiagramNode(slide, "XSum split\nmaterialization", {
    x: 1.52,
    y: 2.27,
    w: 1.84,
    h: 0.88,
    fontSize: 13.5,
  });
  addDiagramNode(slide, "Fine-tuned BART\n+ public baseline", {
    x: 3.84,
    y: 2.27,
    w: 2.18,
    h: 0.88,
    fontSize: 13.5,
  });
  addDiagramNode(slide, "Beam candidate\nsummaries", {
    x: 6.38,
    y: 2.27,
    w: 1.76,
    h: 0.88,
    fontSize: 13.5,
  });
  addDiagramNode(slide, "Weight\nsearch", {
    x: 8.52,
    y: 2.27,
    w: 1.34,
    h: 0.88,
    fontSize: 13.5,
    fillColor: "FBECD9",
  });
  addDiagramNode(slide, "Evaluation,\naudit,\nreport", {
    x: 10.2,
    y: 2.27,
    w: 1.26,
    h: 0.88,
    fontSize: 13.2,
    fillColor: "E8F6EC",
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 3.36,
    y: 2.71,
    w: 0.48,
    h: 0,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 6.02,
    y: 2.71,
    w: 0.36,
    h: 0,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 8.14,
    y: 2.71,
    w: 0.38,
    h: 0,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 9.86,
    y: 2.71,
    w: 0.34,
    h: 0,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 5.42,
    y: 3.76,
    w: 4.18,
    h: 1.22,
    rectRadius: 0.06,
    line: { color: COLORS.berkeleyBlue, width: 1.6 },
    fill: { color: "F9FAFB" },
  });
  slide.addText("Factuality scoring", {
    x: 5.78,
    y: 3.92,
    w: 3.46,
    h: 0.24,
    fontFace: "Liberation Sans",
    fontSize: 13.5,
    bold: true,
    color: "1F2937",
    align: "center",
    margin: 0,
  });
  addDiagramChip(slide, "Support", {
    x: 5.64,
    y: 4.32,
    w: 0.8,
    h: 0.38,
    fontSize: 10.8,
  });
  addDiagramChip(slide, "Consistency", {
    x: 6.52,
    y: 4.32,
    w: 1.18,
    h: 0.38,
    fontSize: 9.8,
  });
  addDiagramChip(slide, "Entity\ngrounding", {
    x: 7.82,
    y: 4.32,
    w: 1.48,
    h: 0.38,
    fontSize: 9.2,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 7.26,
    y: 3.15,
    w: 0,
    h: 0.65,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 8.92,
    y: 4.02,
    w: 0.28,
    h: -1.0,
    line: { color: COLORS.berkeleyBlue, width: 2, endArrowType: "triangle" },
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.82,
    y: 5.34,
    w: 6.0,
    h: 0.82,
    rectRadius: 0.06,
    line: { color: COLORS.line, width: 1 },
    fill: { color: COLORS.panel },
  });
  slide.addText("Scoring signals", {
    x: 1.0,
    y: 5.5,
    w: 5.64,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 12.8,
    bold: true,
    color: COLORS.berkeleyBlueLight,
    margin: 0,
  });
  slide.addText("Support, consistency, and entity grounding are scored for each candidate summary.", {
    x: 1.0,
    y: 5.76,
    w: 5.64,
    h: 0.22,
    fontFace: "Liberation Sans",
    fontSize: 11.9,
    color: COLORS.text,
    valign: "top",
    margin: 0,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.02,
    y: 5.34,
    w: 5.2,
    h: 0.82,
    rectRadius: 0.06,
    line: { color: COLORS.line, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Selection rule", {
    x: 7.2,
    y: 5.5,
    w: 4.84,
    h: 0.2,
    fontFace: "Liberation Sans",
    fontSize: 12.8,
    bold: true,
    color: COLORS.berkeleyBlueLight,
    margin: 0,
  });
  slide.addText("Validation tunes the weights once; the chosen setting is then evaluated once on test.", {
    x: 7.2,
    y: 5.76,
    w: 4.84,
    h: 0.22,
    fontFace: "Liberation Sans",
    fontSize: 11.9,
    color: COLORS.text,
    valign: "top",
    margin: 0,
  });
  slide.addText(
    "Beam sizes 4, 8, and 16 were explored; the winner was a factuality-heavy beam-16 setting.",
    {
      x: 0.82,
      y: 6.22,
      w: 11.2,
      h: 0.22,
      fontFace: "Liberation Sans",
      fontSize: 12.5,
      color: COLORS.muted,
      italic: true,
      margin: 0,
    },
  );
  addNotes(
    slide,
    `
Timing: 0:55

Script:
This slide shows the full method. Starting on the left, I materialize the bounded XSum split and fine-tune BART, while keeping the public baseline for comparison. Then I generate multiple beam candidate summaries for each article. The lower box is the factuality-scoring module that scores every candidate on support, consistency, and entity grounding. I then run weight search on the validation split to find a good operating point, and I evaluate that chosen setting once on test and in the audit. The important point is that the intervention happens after generation. I am not replacing the summarizer. I am choosing among its candidates more carefully.
    `,
  );
  finalizeSlide(slide);
}

// Slide 5: main result
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Results",
    "Reranking improves factuality, with a modest ROUGE trade-off",
    "The chosen point sits near the high-factuality knee, not the highest-ROUGE corner.",
    5,
  );
  addMetricCard(slide, "Factuality composite", "0.331", "0.434", "+0.103 on bounded test split", {
    x: 0.8,
    y: 1.95,
    w: 3.05,
    h: 1.5,
    valueColor: COLORS.success,
    deltaColor: COLORS.success,
  });
  addMetricCard(slide, "ROUGE-Lsum", "0.359", "0.339", "-0.020 ROUGE-Lsum trade-off", {
    x: 4.05,
    y: 1.95,
    w: 3.05,
    h: 1.5,
    valueColor: COLORS.warning,
    deltaColor: COLORS.warning,
  });
  addInfoCard(slide, "Bootstrap deltas", "Factuality CI: [0.082, 0.125]\nROUGE CI: [-0.033, -0.006]", {
    x: 0.8,
    y: 3.72,
    w: 6.15,
    h: 0.95,
    fontSize: 14,
    fillColor: COLORS.panel,
  });
  addInfoCard(slide, "Chosen point", "Beam 16 winner; factuality-heavy fusion beat likelihood-heavy settings.", {
    x: 0.8,
    y: 4.9,
    w: 6.15,
    h: 0.85,
    fontSize: 13.5,
    fillColor: COLORS.white,
  });
  const frontierPath = path.join(figuresDir, "pareto_frontier.png");
  slide.addImage({
    path: frontierPath,
    ...imageSizingContain(frontierPath, 7.12, 1.85, 5.42, 4.95),
  });
  slide.addText("Selected final stays near the high-factuality knee rather than the highest-ROUGE point.", {
    x: 7.18,
    y: 6.18,
    w: 5.2,
    h: 0.22,
    fontFace: "Liberation Sans",
    fontSize: 12.5,
    color: COLORS.muted,
    italic: true,
    margin: 0,
  });
  addNotes(
    slide,
    `
Timing: 1:20

Script:
Here is the main result. The baseline factuality composite was 0.331, and the reranked system increased that to 0.434. At the same time, ROUGE-Lsum went from 0.359 to 0.339, so the trade-off was about minus 0.02 ROUGE for plus 0.103 factuality. I want to be explicit that this was a deliberate operating-point choice, not an accident. On the frontier, I selected a point near the high-factuality knee rather than the highest-ROUGE corner. The bootstrap intervals were also directionally stable, which gave me more confidence that this was a real bounded improvement. A bounded MiniCheck check on the qualitative subset moved in the same direction, so the result is not resting on only one metric.
    `,
  );
  finalizeSlide(slide);
}

// Slide 6: qualitative analysis
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Analysis",
    "The main remaining failure mode is entity distortion",
    "The reranker helps, but most of the remaining misses are still entity errors.",
    6,
  );
  const errorPath = path.join(figuresDir, "error_taxonomy.png");
  slide.addImage({
    path: errorPath,
    ...imageSizingContain(errorPath, 0.72, 2.0, 5.95, 3.95),
  });
  addBulletList(
    slide,
    [
      "24-example stratified review with Codex / AI-assisted expert adjudication.",
      "Outcome split is balanced: reranker 8, baseline 8, tie or close 8.",
      "Entity distortion dominates the remaining errors (13 of 24); number/date and polarity are smaller.",
    ],
    { x: 6.95, y: 2.02, w: 5.2, h: 3.1, fontSize: 17.2, paraSpaceAfterPt: 8 },
  );
  addInfoCard(
    slide,
    "Bounded claim",
    "Directional improvement, not benchmark-scale proof: this supports the approach, not a claim about XSum overall.",
    { x: 6.95, y: 5.28, w: 5.2, h: 1.02, fontSize: 13.2, fillColor: COLORS.panel },
  );
  addNotes(
    slide,
    `
Timing: 0:55

Script:
I also wanted to understand what still goes wrong. I did a 24-example stratified qualitative review with Codex and AI-assisted expert adjudication. The outcome split was balanced between reranker wins, baseline wins, and ties or close calls, but the dominant remaining error type was entity distortion. In other words, the system is still most vulnerable when a named entity is wrong, swapped, or unsupported. This also matches the refinement result in the report: adding entity support helped, but only modestly. So the conclusion is not that factuality is solved. The conclusion is that reranking helps overall, but entity grounding remains the main bottleneck.
    `,
  );
  finalizeSlide(slide);
}

// Slide 7: takeaways
{
  const slide = pptx.addSlide();
  addContentFrame(
    slide,
    "Takeaways",
    "Reranking helps, but entity grounding is still the bottleneck",
    "Useful gain now; the strongest next step is better entity preservation.",
    7,
  );
  addNumberedTakeaway(slide, 1, "Main result", "A lightweight reranker materially improves factuality on this bounded XSum run.", {
    x: 0.82,
    y: 1.95,
    w: 5.45,
    h: 1.08,
  });
  addNumberedTakeaway(
    slide,
    2,
    "Main limitation",
    "Entity-level mistakes still dominate when all beam candidates drift toward the same wrong fact.",
    {
      x: 0.82,
      y: 3.22,
      w: 5.45,
      h: 1.08,
    },
  );
  addNumberedTakeaway(
    slide,
    3,
    "Next iteration",
    "Broaden candidate diversity and add stronger entity-preservation constraints before scaling the evaluation.",
    {
      x: 0.82,
      y: 4.49,
      w: 5.45,
      h: 1.08,
    },
  );
  addInfoCard(slide, "Why this matters", "It shows that a small, interpretable post-generation layer can improve factual quality without retraining a whole new architecture.", {
    x: 6.65,
    y: 2.05,
    w: 5.05,
    h: 1.4,
    fontSize: 15,
    fillColor: COLORS.white,
  });
  addInfoCard(slide, "If I had more time", "Larger bounded splits\nmore diverse candidate sets\nstronger entity-aware constraints\nexternal factuality checks", {
    x: 6.65,
    y: 3.8,
    w: 5.05,
    h: 1.72,
    fontSize: 14.5,
    fillColor: COLORS.panel,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.82,
    y: 6.0,
    w: 10.88,
    h: 0.48,
    rectRadius: 0.05,
    line: { color: COLORS.gold, width: 1.2 },
    fill: { color: "FFF8E6" },
  });
  slide.addText(
    "Final message: reranking improves factuality meaningfully, but entity grounding remains the hardest problem.",
    {
      x: 1.04,
      y: 6.12,
      w: 10.45,
      h: 0.2,
      fontFace: "Liberation Sans",
      fontSize: 13.5,
      bold: true,
      color: COLORS.berkeleyBlue,
      margin: 0,
    },
  );
  addNotes(
    slide,
    `
Timing: 0:45

Script:
I want to end on three points. First, a lightweight reranker materially improved factuality on this bounded XSum run. Second, the main limitation is still entity-level error, especially when all of the beam candidates drift toward the same wrong fact. Third, the most promising next step is to increase candidate diversity and add stronger entity-preservation constraints. So the short version of the project is: reranking helps, but entity grounding is still the hardest problem.
    `,
  );
  finalizeSlide(slide);
}

// Slide 8: questions
{
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.white };
  slide.addText("Questions?", {
    x: 0,
    y: 2.45,
    w: 13.333,
    h: 0.5,
    fontFace: "Liberation Sans",
    fontSize: 26,
    bold: true,
    color: "5B5B5B",
    align: "center",
    margin: 0,
  });
  slide.addImage({
    path: logoPath,
    ...imageSizingContain(logoPath, 0.58, 6.65, 2.45, 0.52),
  });
  addNotes(
    slide,
    `
Timing: 0:05

Script:
Thank you. I’m happy to take questions.
    `,
  );
  finalizeSlide(slide);
}

pptx.writeFile({ fileName: outputPath });
