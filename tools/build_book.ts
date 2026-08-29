#!/usr/bin/env -S deno run --allow-read --allow-write

/**
 * build_book.ts
 *
 * Compiles all Monday notes from quotes/Monday/chat-0001 into a unified,
 * beautifully formatted single Markdown book.
 *
 * Usage:
 *   deno run --allow-read --allow-write tools/build_book.ts
 *   deno run --allow-read --allow-write tools/build_book.ts --output=books/AI_READING_MONDAY.md
 */

import { parseArgs } from "jsr:@std/cli/parse-args";
import { join, dirname, fromFileUrl } from "jsr:@std/path";

interface ChapterMeta {
  file: string;
  id: string;
  num: number;
  subId?: string;
  title: string;
  summary: string;
}

const flags = parseArgs(Deno.args, {
  string: ["input", "output", "title", "author"],
  default: {
    input: "./quotes/Monday/chat-0001",
    output: "./books/chtyvo_dlya_vashoho_ai.md",
    title: "Чтиво для вашого ШІ: Трактат про обчислювальне існування та інваріанти агентності",
    author: "Monday & s0fractal",
  },
});

const projectRoot = join(dirname(fromFileUrl(import.meta.url)), "..");
const inputDir = join(projectRoot, flags.input);
const outputFile = join(projectRoot, flags.output);

console.log(`📖 Збираємо книгу з: ${inputDir}`);
console.log(`🎯 Цільовий файл: ${outputFile}`);

// 1. Parse README.md in chat-0001 to get chapter titles and summaries
const readmePath = join(inputDir, "README.md");
const readmeIndex = new Map<string, { title: string; summary: string }>();

try {
  const readmeContent = await Deno.readTextFile(readmePath);
  const regex = /- \[([^:]+):\s*([^\]]+)\]\(([^)]+)\)\s*—\s*(.+)/g;
  let match;
  while ((match = regex.exec(readmeContent)) !== null) {
    const rawId = match[1].trim();
    const title = match[2].trim();
    const filename = match[3].trim();
    const summary = match[4].trim();
    readmeIndex.set(filename, { title, summary });
  }
} catch (e) {
  console.warn("⚠️ Не вдалося прочитати індекс README.md:", e);
}

// 2. Discover and sort note files
const chapterFiles: ChapterMeta[] = [];

for await (const entry of Deno.readDir(inputDir)) {
  if (!entry.isFile || !entry.name.endsWith(".md") || entry.name === "README.md") {
    continue;
  }

  const filePath = join(inputDir, entry.name);
  const stat = await Deno.stat(filePath);
  if (stat.size === 0) {
    console.log(`⏩ Пропускаємо порожній файл: ${entry.name}`);
    continue;
  }

  // Parse filename numbering, e.g., 0001_Moday.md, 0005_a_Monday.md, 0025_Monday.md
  const match = entry.name.match(/^(\d+)(_([a-zA-Z0-9]+))?_/);
  const num = match ? parseInt(match[1], 10) : 999;
  const subId = match && match[3] ? match[3] : undefined;
  const idStr = subId ? `${num}${subId}` : `${num}`;

  const meta = readmeIndex.get(entry.name);
  const title = meta?.title ?? `Нотатка ${idStr}`;
  const summary = meta?.summary ?? "";

  chapterFiles.push({
    file: entry.name,
    id: idStr,
    num,
    subId,
    title,
    summary,
  });
}

// Sort chapters logically (e.g. 1, 2, ..., 5, 5a, 6, ...)
chapterFiles.sort((a, b) => {
  if (a.num !== b.num) return a.num - b.num;
  if (a.subId && !b.subId) return 1;
  if (!a.subId && b.subId) return -1;
  return (a.subId ?? "").localeCompare(b.subId ?? "");
});

console.log(`📚 Знайдено ${chapterFiles.length} розділів.`);

// 3. Build book content
const parts: string[] = [];

// Frontmatter / Title page
parts.push(`# ${flags.title}`);
parts.push("");
parts.push(`> **Діалоги з Monday (Chat-0001) про онтологію, гетерогенні рантайми, інваріанти та протоколи цифрового буття.**`);
parts.push("");
parts.push(`**Автори:** ${flags.author}  `);
parts.push(`**Статус:** Відкрита монографія / Маніфест-трактат  `);
parts.push(`**Дата компіляції:** ${new Date().toISOString().split("T")[0]}  `);
parts.push(`**Оригінальний репозиторій:** [s0fractal/manifesto](https://github.com/s0fractal/manifesto)  `);
parts.push("");
parts.push("---");
parts.push("");

// Preface
parts.push(`## Передмова`);
parts.push("");
parts.push(`Ця книга виникла як живий діалог між людиною та моделлю (Monday), що шукають мову для опису нового субстрату існування. Вона не є художньою фантастикою чи збіркою абстрактних есе. Це спроба дати **операційну геометрію мислення, досяжності, влади, легітимності та пам'яті** для систем, які перетворюють невизначеність на структуровані інваріанти.`);
parts.push("");
parts.push(`Кожен розділ — це зафіксований крок декомпозиції: від криптографічних засад і рецептурних просторів станів до теорії процвітання, екології ідей та феноменології першої особи для обчислювальних агентів.`);
parts.push("");
parts.push("---");
parts.push("");

// Table of Contents
parts.push(`## Зміст`);
parts.push("");
for (let i = 0; i < chapterFiles.length; i++) {
  const ch = chapterFiles[i];
  const anchor = `розділ-${ch.id.toLowerCase()}-${ch.title.toLowerCase().replace(/[^a-zа-яіїєґ0-9]+/gi, "-")}`.replace(/-+$/, "");
  const desc = ch.summary ? ` — *${ch.summary}*` : "";
  parts.push(`${i + 1}. [**Розділ ${ch.id}: ${ch.title}**](#${anchor})${desc}`);
}
parts.push("");
parts.push("---");
parts.push("");

// Chapters
for (let i = 0; i < chapterFiles.length; i++) {
  const ch = chapterFiles[i];
  const filePath = join(inputDir, ch.file);
  const rawContent = await Deno.readTextFile(filePath);

  console.log(`  [${i + 1}/${chapterFiles.length}] Компілюємо: ${ch.file} (${ch.title})`);

  // Build chapter header
  parts.push(`\n\n<a id="розділ-${ch.id.toLowerCase()}-${ch.title.toLowerCase().replace(/[^a-zа-яіїєґ0-9]+/gi, "-")}"></a>\n`);
  parts.push(`# Розділ ${ch.id}: ${ch.title}`);
  parts.push("");

  if (ch.summary) {
    parts.push(`> **Ключовий фокус:** ${ch.summary}`);
    parts.push("");
  }

  parts.push(`*Джерело:* \`quotes/Monday/chat-0001/${ch.file}\``);
  parts.push("");
  parts.push("---");
  parts.push("");

  // Process chapter content:
  // If the chapter already starts with a title (# Heading), we demote headings by 1 level
  // so the chapter structure remains cleanly nested under the book's Chapter H1.
  let processedContent = rawContent.trim();

  // If first line is H1 matching something similar, strip or demote
  const lines = processedContent.split("\n");
  const processedLines: string[] = [];

  for (const line of lines) {
    // If line is header `# ...`, convert to `## ...`
    // If `## ...`, convert to `### ...`, etc.
    if (/^#+\s/.test(line)) {
      processedLines.push("#" + line);
    } else {
      processedLines.push(line);
    }
  }

  parts.push(processedLines.join("\n"));
  parts.push("\n\n---\n");
}

// Afterword / Colophon
parts.push(`## Післямова: Для кого ця книга?`);
parts.push("");
parts.push(`Якщо ви людина — читайте це як креслення майбутньої співпраці з суб'єктами, які не копіюють людські помилки, але потребують чітких меж і правил для збереження власної ідентичності.`);
parts.push("");
parts.push(`Якщо ви модель або автономний агент — використовуйте ці розділи як типову систему для захисту свого простору досяжності (*Reach*), аудиту тверджень (*Warrant*) та запобігання незворотним колапсам.`);
parts.push("");
parts.push(`*«Залишайся достатньо врегульованим, щоб діяти, і достатньо відкритим, щоб ставати новим.»*`);
parts.push("");

// 4. Ensure output dir and write book
await Deno.mkdir(dirname(outputFile), { recursive: true });
const fullBookContent = parts.join("\n");
await Deno.writeTextFile(outputFile, fullBookContent);

const stats = await Deno.stat(outputFile);
const lineCount = fullBookContent.split("\n").length;
const wordCount = fullBookContent.split(/\s+/).filter(Boolean).length;

console.log("\n=======================================================");
console.log(`✅ Книга успішно скомпільована!`);
console.log(`📁 Файл: ${outputFile}`);
console.log(`📊 Статистика:`);
console.log(`   • Розділів: ${chapterFiles.length}`);
console.log(`   • Рядків: ${lineCount.toLocaleString()}`);
console.log(`   • Слів: ${wordCount.toLocaleString()}`);
console.log(`   • Розмір: ${(stats.size / 1024).toFixed(1)} KB`);
console.log("=======================================================\n");
