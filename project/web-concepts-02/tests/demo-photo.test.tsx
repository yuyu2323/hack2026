import { afterEach, expect, test, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { PhotoPicker } from "../src/shared/photos";
afterEach(() => { cleanup(); vi.restoreAllMocks(); });
test("public sample uses the same file selection flow and carries an AI label", async () => {
  URL.createObjectURL = vi.fn(() => "blob:test"); URL.revokeObjectURL = vi.fn();
  vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(new Blob(["synthetic"], { type: "image/png" })));
  const set = vi.fn();
  render(<PhotoPicker files={[]} set={set} demoSample />);
  fireEvent.click(screen.getByRole("button", { name: "시연 사진 사용" }));
  await waitFor(() => expect(set).toHaveBeenCalledOnce());
  const file = set.mock.calls[0][0][0] as File;
  expect(file.name).toBe("AI 생성 시연 사진.png");
  expect(file.type).toBe("image/png");
  expect(file.size).toBeGreaterThan(0);
});
test("normal file picker does not offer public sample", () => {
  render(<PhotoPicker files={[]} set={() => {}} />);
  expect(screen.queryByRole("button", { name: "시연 사진 사용" })).toBeNull();
});
