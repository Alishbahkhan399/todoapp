import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = path.join(projectRoot, "dist");
const sourceDirectory = path.join(projectRoot, "static");
const htmlPath = path.join(sourceDirectory, "index.html");
const backendLinksPath = path.join(sourceDirectory, "js", "backend-links.js");
let backendUrl = process.env.BACKEND_URL?.trim() ?? "";

if (backendUrl) {
  const parsedBackendUrl = new URL(backendUrl);
  if (!( ["https:", "http:"].includes(parsedBackendUrl.protocol))) {
    throw new Error("BACKEND_URL must use http or https.");
  }
  backendUrl = backendUrl.replace(/\/+$/, "");
}

const backendLinks = await readFile(backendLinksPath, "utf8");
if (!backendLinks.includes("__BACKEND_URL__")) {
  throw new Error("The frontend is missing its BACKEND_URL placeholder.");
}

await rm(outputDirectory, { recursive: true, force: true });
await mkdir(outputDirectory, { recursive: true });
await cp(htmlPath, path.join(outputDirectory, "index.html"));
await cp(path.join(sourceDirectory, "css"), path.join(outputDirectory, "css"), { recursive: true });
await cp(path.join(sourceDirectory, "js"), path.join(outputDirectory, "js"), { recursive: true });
await writeFile(
  path.join(outputDirectory, "js", "backend-links.js"),
  backendLinks.replace("__BACKEND_URL__", JSON.stringify(backendUrl)),
);

console.log(`Built static frontend in ${outputDirectory}`);