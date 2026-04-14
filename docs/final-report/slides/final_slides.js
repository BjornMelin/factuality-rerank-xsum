const path = require("path");
const PptxGenJS = require("pptxgenjs");
const { imageSizingContain } = require("./pptxgenjs_helpers/image");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Bjorn Melin";
pptx.company = "UC Berkeley MIDS";
pptx.subject = "DS266 final project presentation";
pptx.title = "Factuality-Aware Reranking for Extreme Summarization";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Arial",
  bodyFontFace: "Arial",
  lang: "en-US",
};

const COLORS = {
  bg: "F7F3EA",
  ink: "1F2A30",
  teal: "0E5A63",
  rust: "B35C3F",
  gold: "C8942A",
  soft: "E6DED0",
  white: "FFFFFF",
  muted: "5E6A70",
};

const figuresDir = path.resolve(__dirname, "../../../outputs/final/figures");
const outputPath = path.resolve(
  __dirname,
  "../../../outputs/final/submission/final_slides.pptx",
);

function addChrome(slide, eyebrow, title, subtitle = "") {
  slide.background = { color: COLORS.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.42,
    line: { color: COLORS.teal, transparency: 100 },
    fill: { color: COLORS.teal },
  });
  slide.addText(eyebrow, {
    x: 0.6,
    y: 0.58,
    w: 5.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 14,
    bold: true,
    color: COLORS.rust,
    charSpace: 1.2,
    allCaps: true,
  });
  slide.addText(title, {
    x: 0.6,
    y: 0.9,
    w: 9.7,
    h: 0.5,
    fontFace: "Arial",
    fontSize: 26,
    bold: true,
    color: COLORS.ink,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6,
      y: 1.62,
      w: 11.2,
      h: 0.3,
      fontFace: "Arial",
      fontSize: 11.5,
      color: COLORS.muted,
      italic: true,
    });
  }
  slide.addShape(pptx.ShapeType.line, {
    x: 0.6,
    y: 2.0,
    w: 12.0,
    h: 0,
    line: { color: COLORS.soft, width: 1.3 },
  });
}

function addFooter(slide, text) {
  slide.addText(text, {
    x: 0.6,
    y: 7.0,
    w: 12.0,
    h: 0.25,
    fontFace: "Arial",
    fontSize: 9,
    color: COLORS.muted,
    align: "right",
  });
}

function addBullets(slide, items, opts = {}) {
  const runs = [];
  items.forEach((item, index) => {
    runs.push({
      text: item,
      options: {
        breakLine: index !== items.length - 1,
        bullet: { indent: 14 },
      },
    });
  });
  slide.addText(runs, {
    x: opts.x,
    y: opts.y,
    w: opts.w,
    h: opts.h,
    fontFace: "Arial",
    fontSize: opts.fontSize || 16,
    color: COLORS.ink,
    breakLine: true,
    valign: "top",
    paraSpaceAfterPt: 10,
    margin: 2,
  });
}

function finalizeSlide(slide) {
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: COLORS.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 7.5,
    line: { color: COLORS.bg, transparency: 100 },
    fill: { color: COLORS.bg },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.55,
    line: { color: COLORS.teal, transparency: 100 },
    fill: { color: COLORS.teal },
  });
  slide.addText("Factuality-Aware Reranking for Extreme Summarization", {
    x: 0.7,
    y: 1.0,
    w: 7.7,
    h: 1.15,
    fontFace: "Arial",
    fontSize: 28,
    bold: true,
    color: COLORS.ink,
    valign: "mid",
  });
  slide.addText("Bounded XSum study with fine-tuned BART, factuality-aware reranking, and explicit audit validation", {
    x: 0.72,
    y: 2.18,
    w: 7.9,
    h: 0.72,
    fontFace: "Arial",
    fontSize: 15,
    color: COLORS.muted,
    italic: true,
  });
  slide.addText("Bjorn Melin\nUC Berkeley MIDS", {
    x: 0.72,
    y: 5.95,
    w: 4.0,
    h: 0.65,
    fontFace: "Arial",
    fontSize: 15,
    color: COLORS.ink,
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.65,
    y: 1.15,
    w: 3.95,
    h: 4.95,
    rectRadius: 0.08,
    line: { color: COLORS.soft, width: 1.2 },
    fill: { color: COLORS.white },
  });
  slide.addText("Headline trade-off", {
    x: 9.0,
    y: 1.45,
    w: 2.8,
    h: 0.3,
    fontFace: "Arial",
    fontSize: 13,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("Factuality composite", {
    x: 9.0,
    y: 2.0,
    w: 2.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 12,
    color: COLORS.muted,
  });
  slide.addText("0.3324 → 0.4420", {
    x: 9.0,
    y: 2.28,
    w: 2.95,
    h: 0.4,
    fontFace: "Arial",
    fontSize: 22,
    bold: true,
    color: COLORS.teal,
  });
  slide.addText("ROUGE-Lsum", {
    x: 9.0,
    y: 3.05,
    w: 2.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 12,
    color: COLORS.muted,
  });
  slide.addText("0.3569 → 0.3398", {
    x: 9.0,
    y: 3.33,
    w: 2.95,
    h: 0.4,
    fontFace: "Arial",
    fontSize: 22,
    bold: true,
    color: COLORS.rust,
  });
  slide.addText("Bounded scope", {
    x: 9.0,
    y: 4.18,
    w: 2.8,
    h: 0.24,
    fontFace: "Arial",
    fontSize: 12,
    color: COLORS.muted,
  });
  slide.addText("train=128\nval=64/128\ntest=128\naudit=24", {
    x: 9.0,
    y: 4.45,
    w: 2.6,
    h: 1.0,
    fontFace: "Arial",
    fontSize: 16,
    bold: true,
    color: COLORS.ink,
  });
  addFooter(slide, "DS266 final project · April 2026");
  finalizeSlide(slide);
}

// Slide 2
{
  const slide = pptx.addSlide();
  addChrome(
    slide,
    "Problem and Setup",
    "Why factuality is the real XSum problem",
    "The repo now runs the full bounded CLI chain end to end.",
  );
  addBullets(slide, [
    "XSum encourages aggressive compression, so fluent summaries can still add unsupported facts.",
    "ROUGE alone cannot tell whether the generated sentence is grounded in the article.",
    "I keep the public facebook/bart-large-xsum checkpoint as the explicit baseline comparator.",
    "Question: can reranking trade a small amount of ROUGE for materially stronger factuality?",
  ], { x: 0.7, y: 2.25, w: 5.5, h: 3.8, fontSize: 16 });
  slide.addImage({
    path: path.join(figuresDir, "pipeline_diagram.png"),
    ...imageSizingContain(path.join(figuresDir, "pipeline_diagram.png"), 6.55, 2.18, 6.1, 3.95),
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.7,
    y: 6.35,
    w: 5.7,
    h: 0.48,
    rectRadius: 0.05,
    line: { color: COLORS.soft, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Bounded data splits: train=128, val_tune=64, val_full=128, test=128", {
    x: 6.95,
    y: 6.48,
    w: 5.25,
    h: 0.18,
    fontFace: "Arial",
    fontSize: 11,
    color: COLORS.ink,
    align: "center",
  });
  addFooter(slide, "Public BART baseline preserved as the honest comparator");
  finalizeSlide(slide);
}

// Slide 3
{
  const slide = pptx.addSlide();
  addChrome(
    slide,
    "Method",
    "Proposal-faithful pipeline, not a new model family",
    "Fine-tuned generator plus factuality-aware candidate selection.",
  );
  addBullets(slide, [
    "Fine-tune BART on the bounded train split and export the best checkpoint.",
    "Generate beam candidates with sizes 4, 8, and 16.",
    "Score each candidate with generation likelihood, SummaC-style support, FactCC-style consistency, and entity support.",
    "Search the weight space on validation once, then evaluate the selected operating point on the test split.",
  ], { x: 0.7, y: 2.25, w: 5.1, h: 4.2, fontSize: 15.5 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.25,
    y: 2.35,
    w: 6.2,
    h: 2.65,
    rectRadius: 0.05,
    line: { color: COLORS.soft, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Metric", {
    x: 6.55,
    y: 2.58,
    w: 2.2,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("Baseline", {
    x: 9.0,
    y: 2.58,
    w: 1.2,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
    align: "center",
  });
  slide.addText("Final", {
    x: 10.8,
    y: 2.58,
    w: 1.0,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
    align: "center",
  });
  const metricRows = [
    ["ROUGE-Lsum", "0.3569", "0.3398"],
    ["Factuality composite", "0.3324", "0.4420"],
    ["Audit consistent rate", "0.0000", "0.0417"],
    ["MiniCheck support rate", "0.3333", "0.4583"],
  ];
  metricRows.forEach((row, idx) => {
    const y = 2.95 + idx * 0.44;
    slide.addShape(pptx.ShapeType.line, {
      x: 6.5,
      y: y - 0.08,
      w: 5.65,
      h: 0,
      line: { color: COLORS.soft, width: 0.8 },
    });
    slide.addText(row[0], {
      x: 6.55,
      y,
      w: 2.35,
      h: 0.18,
      fontFace: "Arial",
      fontSize: 12.5,
      color: COLORS.ink,
    });
    slide.addText(row[1], {
      x: 8.95,
      y,
      w: 1.35,
      h: 0.18,
      fontFace: "Arial",
      fontSize: 12.5,
      bold: true,
      color: COLORS.ink,
      align: "center",
    });
    slide.addText(row[2], {
      x: 10.7,
      y,
      w: 1.25,
      h: 0.18,
      fontFace: "Arial",
      fontSize: 12.5,
      bold: true,
      color: COLORS.teal,
      align: "center",
    });
  });
  slide.addText("Bootstrap deltas", {
    x: 6.35,
    y: 5.35,
    w: 2.4,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("ROUGE-Lsum CI: [-0.0310, -0.0029]\nFactuality CI: [0.0887, 0.1321]", {
    x: 6.35,
    y: 5.62,
    w: 5.9,
    h: 0.7,
    fontFace: "Arial",
    fontSize: 16,
    color: COLORS.ink,
  });
  slide.addText("Interpretation: clear factuality win, modest overlap cost.", {
    x: 6.35,
    y: 6.42,
    w: 5.6,
    h: 0.3,
    fontFace: "Arial",
    fontSize: 13.5,
    italic: true,
    color: COLORS.muted,
  });
  addFooter(slide, "MiniCheck is reported only on the 24-row audit subset");
  finalizeSlide(slide);
}

// Slide 4
{
  const slide = pptx.addSlide();
  addChrome(
    slide,
    "Search and Refinement",
    "The selected operating point is factuality-heavy by design",
    "Validation search chooses the operating point; test is used once for the final comparison.",
  );
  slide.addImage({
    path: path.join(figuresDir, "pareto_frontier.png"),
    ...imageSizingContain(path.join(figuresDir, "pareto_frontier.png"), 0.72, 2.2, 6.3, 4.25),
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.35,
    y: 2.28,
    w: 5.25,
    h: 1.35,
    rectRadius: 0.05,
    line: { color: COLORS.soft, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Selected config", {
    x: 7.7,
    y: 2.55,
    w: 2.4,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("custom_0097 · beam 16\nweights = [0.0, 0.75, 1.0, 0.5]", {
    x: 7.7,
    y: 2.86,
    w: 4.4,
    h: 0.52,
    fontFace: "Arial",
    fontSize: 18,
    bold: true,
    color: COLORS.ink,
  });
  addBullets(slide, [
    "Likelihood is not the final decision signal; factuality features dominate the winning fusion.",
    "The explicit refinement iteration is entity support, added after inspecting failure patterns.",
    "Ablation: factuality composite rises from 0.4061 to 0.4106 when entity support is added.",
    "This is an incremental but justified refinement, not a late-stage redesign.",
  ], { x: 7.3, y: 4.05, w: 5.2, h: 2.45, fontSize: 15.5 });
  addFooter(slide, "Entity distortion remains the main remaining error category");
  finalizeSlide(slide);
}

// Slide 5
{
  const slide = pptx.addSlide();
  addChrome(
    slide,
    "Audit and Limits",
    "Manual inspection kept the project honest",
    "The audit is useful for error slicing and claim control, not for human-label reliability claims.",
  );
  slide.addImage({
    path: path.join(figuresDir, "error_taxonomy.png"),
    ...imageSizingContain(path.join(figuresDir, "error_taxonomy.png"), 0.9, 2.25, 4.8, 3.65),
  });
  addBullets(slide, [
    "24-row stratified Codex / AI-assisted expert adjudication audit with explicit provenance.",
    "Outcome counts: reranker win 8, baseline win 8, tie/close 8.",
    "Dominant remaining failure: entity distortion (12/24), then negation/polarity (6) and number/date errors (5).",
    "MiniCheck on the same subset raises support rate from 0.3333 to 0.4583.",
  ], { x: 5.95, y: 2.28, w: 6.15, h: 3.1, fontSize: 15.2 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 5.95,
    y: 5.55,
    w: 6.05,
    h: 1.05,
    rectRadius: 0.05,
    line: { color: COLORS.soft, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Key limit", {
    x: 6.25,
    y: 5.8,
    w: 1.3,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("This is a bounded study: train=128, test=128, audit=24. The repo is submission-ready, but the claims remain bounded.", {
    x: 6.25,
    y: 6.07,
    w: 5.45,
    h: 0.35,
    fontFace: "Arial",
    fontSize: 13.5,
    color: COLORS.ink,
  });
  addFooter(slide, "Audit wording must remain exact: Codex / AI-assisted expert adjudication");
  finalizeSlide(slide);
}

// Slide 6
{
  const slide = pptx.addSlide();
  addChrome(
    slide,
    "Takeaways",
    "What this project demonstrates and what it does not",
    "Close with the trade-off, not with benchmark inflation.",
  );
  addBullets(slide, [
    "Simple reranking signals materially improve factuality on this bounded XSum run.",
    "Entity support is a useful small refinement, but not a cure for entity-level hallucination.",
    "The strongest remaining failure mode appears when all beam candidates drift toward the same wrong entity or relation.",
    "The repo, report, slides, package, and final outputs now tell one aligned story.",
  ], { x: 0.8, y: 2.25, w: 6.1, h: 3.2, fontSize: 16 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.3,
    y: 2.3,
    w: 5.1,
    h: 3.55,
    rectRadius: 0.06,
    line: { color: COLORS.soft, width: 1 },
    fill: { color: COLORS.white },
  });
  slide.addText("Submission bundle", {
    x: 7.62,
    y: 2.62,
    w: 2.6,
    h: 0.25,
    fontFace: "Arial",
    fontSize: 12,
    bold: true,
    color: COLORS.rust,
    allCaps: true,
    charSpace: 0.8,
  });
  slide.addText("final_report.pdf\nfinal_slides.pptx\nfinal_slides.pdf\nspeaker_notes.md\nfactuality-rerank-xsum.zip", {
    x: 7.62,
    y: 2.95,
    w: 4.3,
    h: 1.8,
    fontFace: "Arial",
    fontSize: 19,
    bold: true,
    color: COLORS.ink,
    breakLine: true,
  });
  slide.addText("Final message: factuality can improve without pretending the ROUGE trade-off disappeared.", {
    x: 7.62,
    y: 5.0,
    w: 4.2,
    h: 0.65,
    fontFace: "Arial",
    fontSize: 14.5,
    italic: true,
    color: COLORS.muted,
  });
  addFooter(slide, "Project closeout: bounded, aligned, and submission-ready");
  finalizeSlide(slide);
}

pptx.writeFile({ fileName: outputPath });
