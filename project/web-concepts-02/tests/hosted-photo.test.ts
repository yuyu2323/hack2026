import { afterEach, expect, test, vi } from "vitest";
import { prepareHostedPhoto, HOSTED_PHOTO_BYTES } from "../src/shared/hosted-photo";

afterEach(() => vi.unstubAllGlobals());

test("small photo keeps its original bytes", async () => {
  const file = new File(["small"], "photo.png", { type: "image/png" });
  expect(await prepareHostedPhoto(file, 5)).toBe(file);
});

test("large photo becomes a bounded JPEG and releases decoded memory", async () => {
  const close = vi.fn();
  vi.stubGlobal("createImageBitmap", vi.fn().mockResolvedValue({ width: 4000, height: 3000, close }));
  const drawImage = vi.fn();
  const canvas = { width: 0, height: 0, getContext: () => ({ fillStyle: "", fillRect: vi.fn(), drawImage }),
    toBlob: (done: (blob: Blob) => void) => done(new Blob(["bounded"], { type: "image/jpeg" })) };
  vi.stubGlobal("document", { createElement: () => canvas });
  const file = new File([new Uint8Array(HOSTED_PHOTO_BYTES)], "large.png", { type: "image/png" });
  const result = await prepareHostedPhoto(file, 5);
  expect(result.type).toBe("image/jpeg");
  expect(result.name).toBe("large.jpg");
  expect(result.size).toBeLessThanOrEqual(Math.floor(HOSTED_PHOTO_BYTES / 5));
  expect(canvas.width).toBe(1800);
  expect(canvas.height).toBe(1350);
  expect(close).toHaveBeenCalledOnce();
});

test("unavailable canvas rejects without sending oversized file", async () => {
  const close = vi.fn();
  vi.stubGlobal("createImageBitmap", vi.fn().mockResolvedValue({ width: 2000, height: 1000, close }));
  vi.stubGlobal("document", { createElement: () => ({ getContext: () => null }) });
  const file = new File([new Uint8Array(HOSTED_PHOTO_BYTES)], "large.png");
  await expect(prepareHostedPhoto(file, 5)).rejects.toThrow();
  expect(close).toHaveBeenCalledOnce();
});
