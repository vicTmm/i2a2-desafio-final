export async function uploadBatch<T>(
  files: readonly T[],
  send: (file: T) => Promise<void>,
): Promise<{ file: T; error: Error }[]> {
  const failures: { file: T; error: Error }[] = [];
  for (const file of files) {
    try {
      await send(file);
    } catch (error) {
      failures.push({
        file,
        error: error instanceof Error ? error : new Error(String(error)),
      });
    }
  }
  return failures;
}
