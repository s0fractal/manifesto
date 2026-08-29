#!/usr/bin/env -S deno run --allow-read --allow-write --allow-run

/**
 * tools/export.ts
 *
 * Recursively exports all Markdown (.md) files in the s0fractal/manifesto
 * repository into a single unified Markdown bundle in `dist/`.
 * Includes active Git commit signature, metadata, and full Table of Contents.
 *
 * Usage:
 *   deno run --allow-read --allow-write --allow-run tools/export.ts
 *   deno run --allow-read --allow-write --allow-run tools/export.ts --output=dist/manifesto_all.md
 */

import { parseArgs } from "jsr:@std/cli/parse-args";
import { join, dirname, relative, fromFileUrl } from "jsr:@std/path";

const flags = parseArgs(Deno.args, {
  string: ["output"],
  default: {
    output: "./dist/manifesto_bundle.md",
  },
});

const projectRoot = join(dirname(fromFileUrl(import.meta.url)), "..");
const outputFile = join(projectRoot, flags.output);

// 1. Get current Git commit info
async function getGitInfo(): Promise<{ hash: string; shortHash: string; date: string; message: string }> {
  try {
    const cmdHash = new Deno.Command("git", {
      args: ["rev-parse", "HEAD"],
      cwd: projectRoot,
    });
    const { stdout: stdoutHash } = await cmdHash.output();
    const hash = new TextDecoder().decode(stdoutHash).trim();

    const cmdShort = new Deno.Command("git", {
      args: ["log", "-1", "--format=%h|%ci|%s"],
      cwd: projectRoot,
    });
    const { stdout: stdoutShort } = await cmdShort.output();
    const [shortHash, date, message] = new TextDecoder().decode(stdoutShort).trim().split("|");

    return {
      hash: hash || "unknown",
      shortHash: shortHash || "unknown",
      date: date || new Date().toISOString(),
      message: message || "",
    };
  } catch (_e) {
    return {
      hash: "unknown",
      shortHash: "unknown",
      date: new Date().toISOString(),
      message: "",
    };
  }
}

// 2. Discover all Markdown files recursively
async function collectMarkdownFiles(dir: string): Promise<string[]> {
  const files: string[] = [];

  for await (const entry of Deno.readDir(dir)) {
    // Ignore .git, dist, node_modules, scratch
    if (
      entry.name === ".git" ||
      entry.name === "dist" ||
      entry.name === "books" ||
      entry.name === "node_modules" ||
      entry.name === "scratch"
    ) {
      continue;
    }

    const fullPath = join(dir, entry.name);
    if (entry.isDirectory) {
      const nested = await collectMarkdownFiles(fullPath);
      files.push(...nested);
    } else if (entry.isFile && entry.name.endsWith(".md")) {
      const stat = await Deno.stat(fullPath);
      if (stat.size > 0) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

// 3. Custom sorting for logical reading order
function sortFiles(files: string[]): string[] {
  const rootOrder = ["README.md", "FLOW.md", "INVARIANT-RECIPES.md"];

  return files.sort((a, b) => {
    const relA = relative(projectRoot, a);
    const relB = relative(projectRoot, b);

    // Root files priority
    const idxA = rootOrder.indexOf(relA);
    const idxB = rootOrder.indexOf(relB);

    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
    if (idxA !== -1) return -1;
    if (idxB !== -1) return 1;

    // Artifacts before quotes
    if (relA.startsWith("artifacts/") && !relB.startsWith("artifacts/")) return -1;
    if (!relA.startsWith("artifacts/") && relB.startsWith("artifacts/")) return 1;

    // Quotes sorting by chapter number
    if (relA.startsWith("quotes/Monday/chat-0001/") && relB.startsWith("quotes/Monday/chat-0001/")) {
      if (relA.endsWith("README.md")) return -1;
      if (relB.endsWith("README.md")) return 1;

      const numA = relA.match(/(\d+)(_([a-zA-Z0-9]+))?_/);
      const numB = relB.match(/(\d+)(_([a-zA-Z0-9]+))?_/);

      if (numA && numB) {
        const valA = parseInt(numA[1], 10);
        const valB = parseInt(numB[1], 10);
        if (valA !== valB) return valA - valB;
        const subA = numA[3] ?? "";
        const subB = numB[3] ?? "";
        return subA.localeCompare(subB);
      }
    }

    return relA.localeCompare(relB);
  });
}

console.log("🔍 Скануємо репозиторій manifesto...");
const gitInfo = await getGitInfo();
const allFiles = await collectMarkdownFiles(projectRoot);
const sortedFiles = sortFiles(allFiles);

console.log(`📦 Знайдено ${sortedFiles.length} валідних Markdown-документів.`);
console.log(`🔗 Git Commit: ${gitInfo.shortHash} (${gitInfo.hash})`);

// 4. Build single bundle content
const parts: string[] = [];

// Frontmatter Header
parts.push("# s0fractal/manifesto — Повний Зведений Експорт");
parts.push("");
parts.push("> **Єдиний зібраний бандл усіх документів, маніфестів, артефактів та діалогів репозиторію.**");
parts.push("");
parts.push(`- **Репозиторій:** [\`s0fractal/manifesto\`](https://github.com/s0fractal/manifesto)`);
parts.push(`- **Активний коміт:** \`${gitInfo.hash}\` (\`${gitInfo.shortHash}\`)`);
parts.push(`- **Останній коміт:** *${gitInfo.message}*`);
parts.push(`- **Дата коміту:** \`${gitInfo.date}\``);
parts.push(`- **Дата експорту:** \`${new Date().toISOString()}\``);
parts.push(`- **Кількість документів:** ${sortedFiles.length}`);
parts.push("");
parts.push("---");
parts.push("");

// Table of Contents
parts.push("## Зміст експорту (Table of Contents)");
parts.push("");

interface DocItem {
  relPath: string;
  anchor: string;
  title: string;
  content: string;
}

const docs: DocItem[] = [];

for (const filePath of sortedFiles) {
  const relPath = relative(projectRoot, filePath);
  const rawContent = await Deno.readTextFile(filePath);

  // Extract first title or use filename
  const firstH1 = rawContent.match(/^#\s+(.+)$/m);
  const firstBold = rawContent.match(/\*\*([^*]+)\*\*/);
  let title = firstH1 ? firstH1[1].trim() : (firstBold ? firstBold[1].trim() : relPath);

  // Clean title
  title = title.replace(/[#*`_]/g, "").trim();
  if (title.length > 90) title = title.substring(0, 87) + "...";

  const anchor = "doc-" + relPath.toLowerCase().replace(/[^a-zа-яіїєґ0-9]+/gi, "-").replace(/-+$/, "");

  docs.push({
    relPath,
    anchor,
    title,
    content: rawContent.trim(),
  });
}

for (let i = 0; i < docs.length; i++) {
  const doc = docs[i];
  parts.push(`${i + 1}. [\`${doc.relPath}\` — **${doc.title}**](#${doc.anchor})`);
}

parts.push("");
parts.push("---");
parts.push("");

// Documents body
for (let i = 0; i < docs.length; i++) {
  const doc = docs[i];
  console.log(`  [${i + 1}/${docs.length}] Експортуємо: ${doc.relPath}`);

  parts.push(`\n<a id="${doc.anchor}"></a>\n`);
  parts.push(`### 📄 Документ [${i + 1}/${docs.length}]: \`${doc.relPath}\``);
  parts.push(`*GitHub посилання:* [\`s0fractal/manifesto/${doc.relPath}\`](https://github.com/s0fractal/manifesto/blob/${gitInfo.hash}/${doc.relPath})`);
  parts.push("");
  parts.push("---");
  parts.push("");
  parts.push(doc.content);
  parts.push("\n\n---\n");
}

// 5. Ensure output directory and write file
await Deno.mkdir(dirname(outputFile), { recursive: true });
const finalContent = parts.join("\n");
await Deno.writeTextFile(outputFile, finalContent);

const stats = await Deno.stat(outputFile);
const lineCount = finalContent.split("\n").length;
const wordCount = finalContent.split(/\s+/).filter(Boolean).length;

console.log("\n=======================================================");
console.log(`✅ Експорт успішно сформовано!`);
console.log(`📁 Цільовий файл: ${outputFile}`);
console.log(`📊 Статистика:`);
console.log(`   • Документів: ${docs.length}`);
console.log(`   • Рядків: ${lineCount.toLocaleString()}`);
console.log(`   • Слів: ${wordCount.toLocaleString()}`);
console.log(`   • Розмір: ${(stats.size / 1024).toFixed(1)} KB`);
console.log(`   • Git Hash: ${gitInfo.shortHash}`);
console.log("=======================================================\n");
