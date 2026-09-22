import { afterEach, expect, test, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { PhotoPicker } from "../src/shared/photos";

afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals(); });
const photo = () => new File(["image"], "clipboard.png", { type: "image/png" });
function paste(target: Element | Document, file = photo()) {
  return fireEvent.paste(target, { clipboardData: { items: [{ kind: "file", type: file.type, getAsFile: () => file }] } });
}
test("pasted image enters the existing photo flow", async () => {
  const set = vi.fn();
  render(<PhotoPicker files={[]} set={set} />);
  expect(paste(document)).toBe(false);
  await waitFor(() => expect(set).toHaveBeenCalledOnce());
  expect(set.mock.calls[0][0][0].name).toBe("clipboard.png");
});
test("text editing and detached picker do not intercept paste", () => {
  const set = vi.fn();
  const { unmount } = render(<><textarea aria-label="메모" /><PhotoPicker files={[]} set={set} /></>);
  expect(paste(screen.getByLabelText("메모"))).toBe(true);
  expect(set).not.toHaveBeenCalled();
  unmount();
  expect(paste(document)).toBe(true);
  expect(set).not.toHaveBeenCalled();
});
test("pasted images retain format and count limits", async () => {
  const set = vi.fn();
  render(<PhotoPicker files={[]} set={set} max={0} />);
  paste(document);
  await screen.findByRole("alert");
  expect(screen.getByRole("alert").textContent).toContain("0장까지");
  expect(set).not.toHaveBeenCalled();
});
test("clipboard button reads only on click and prevents overlapping reads", async () => {
  let finish!: (value: unknown[]) => void;
  const read = vi.fn(() => new Promise<unknown[]>((resolve) => { finish = resolve; }));
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { read } });
  const set = vi.fn();
  render(<PhotoPicker files={[]} set={set} />);
  expect(read).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "클립보드 이미지 붙여넣기" }));
  paste(document);
  finish([{ types: ["image/png"], getType: async () => photo() }]);
  await waitFor(() => expect(set).toHaveBeenCalledOnce());
  expect(read).toHaveBeenCalledOnce();
});
test("clipboard denial gives paste fallback", async () => {
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { read: vi.fn().mockRejectedValue(new Error("denied")) } });
  render(<PhotoPicker files={[]} set={() => {}} />);
  fireEvent.click(screen.getByRole("button", { name: "클립보드 이미지 붙여넣기" }));
  expect((await screen.findByRole("alert")).textContent).toContain("Ctrl+V");
});
