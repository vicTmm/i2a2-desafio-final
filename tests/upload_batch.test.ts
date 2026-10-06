import { test } from "node:test";
import assert from "node:assert/strict";
import { uploadBatch } from "../src/lib/upload.ts";

test("a rejected file does not prevent later uploads; retry sends only failures", async () => {
  const attempts: string[] = [];
  const failures = await uploadBatch(
    ["sandech", "invalid", "tecnogeo", "cortel"],
    async (file) => {
      attempts.push(file);
      if (file === "invalid") throw new Error("PDF inválido");
    },
  );
  assert.deepEqual(attempts, ["sandech", "invalid", "tecnogeo", "cortel"]);
  assert.deepEqual(
    failures.map((f) => f.file),
    ["invalid"],
  );
  assert.equal(failures[0].error.message, "PDF inválido");
  const retries: string[] = [];
  assert.deepEqual(
    await uploadBatch(
      failures.map((f) => f.file),
      async (file) => {
        retries.push(file);
      },
    ),
    [],
  );
  assert.deepEqual(retries, ["invalid"]);
});
