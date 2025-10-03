#!/usr/bin/env node
/**
 * Bundle setup.schema.json and all its dependencies into bundled.schema.json
 * 
 * This script uses @hyperjump/json-schema to resolve all $ref references
 * and create a self-contained schema file.
 */

import { readFile, writeFile, readdir } from "fs/promises";
import { resolve, dirname, join } from "path";
import { fileURLToPath } from "url";
import { registerSchema } from "@hyperjump/json-schema/draft-2020-12";
import { bundle } from "@hyperjump/json-schema/bundle";

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Recursively find all .json files in a directory
 */
async function findJsonFiles(dir: string): Promise<string[]> {
  const files: string[] = [];
  const entries = await readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await findJsonFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.json')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

/**
 * Register a schema file with the given base URI
 */
async function registerSchemaFile(filePath: string, baseUri: string, repoRoot: string): Promise<void> {
  const content = await readFile(filePath, "utf-8");
  const schemaJson = JSON.parse(content);
  
  // Create a URI for this schema based on its relative path from repo root
  const relativePath = filePath.replace(repoRoot + '/', '');
  const schemaUri = `${baseUri}/${relativePath}`;
  
  registerSchema(schemaJson, schemaUri);
}

async function main() {
  try {
    // Paths relative to the repository root
    const repoRoot = resolve(__dirname, "../../..");
    const setupSchemaPath = resolve(repoRoot, "setup.schema.json");
    const protoJsonSchemaDir = resolve(repoRoot, "proto/jsonschema");
    const outputPath = resolve(repoRoot, "bundled.schema.json");

    // Base URI for all schemas
    const baseUri = "https://chirpstack-provisioning.local";

    console.log("Registering all JSON schemas from proto/jsonschema...");
    
    // Find and register all proto JSON schemas
    const protoSchemaFiles = await findJsonFiles(protoJsonSchemaDir);
    console.log(`Found ${protoSchemaFiles.length} proto schema files`);
    
    for (const schemaFile of protoSchemaFiles) {
      await registerSchemaFile(schemaFile, baseUri, repoRoot);
    }

    console.log(`Reading main schema from: ${setupSchemaPath}`);
    
    // Read and register the setup.schema.json file
    const schemaContent = await readFile(setupSchemaPath, "utf-8");
    const schemaJson = JSON.parse(schemaContent);
    
    const setupSchemaUri = `${baseUri}/setup.schema.json`;
    console.log(`Registering main schema with URI: ${setupSchemaUri}`);
    registerSchema(schemaJson, setupSchemaUri);
    
    // Bundle the schema, resolving all external references
    console.log("Bundling schema...");
    const bundledSchema = await bundle(setupSchemaUri, {
      alwaysIncludeDialect: true
    });
    
    // Write the bundled schema to output file
    console.log(`Writing bundled schema to: ${outputPath}`);
    await writeFile(
      outputPath,
      JSON.stringify(bundledSchema, null, 2) + "\n",
      "utf-8"
    );
    
    console.log("✅ Successfully bundled schema!");
    console.log(`Output: ${outputPath}`);
  } catch (error) {
    console.error("❌ Error bundling schema:");
    console.error(error);
    process.exit(1);
  }
}

main();
