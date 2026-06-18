import { mkdir, copyFile, access } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "..", "..", "artifact", "argument_graph.v1.json");
const destDir = resolve(here, "..", "public");
const dest = resolve(destDir, "argument_graph.v1.json");

async function main() {
  await access(source);
  await mkdir(destDir, { recursive: true });
  await copyFile(source, dest);
  console.log(`[copy-artifact] ${source} -> ${dest}`);
}

main().catch((error) => {
  console.error("[copy-artifact] failed:", error.message);
  process.exit(1);
});
