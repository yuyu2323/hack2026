import { afterEach, beforeEach, expect, it, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { api, ApiError, type AccountMe } from "@storeloop/api-client";
import { App } from "../src/app/main";
import { References } from "../src/ofc-admin/Standards";

const account = (role: AccountMe["role"]): AccountMe => ({
  id: "safe-owner",
  login_id: "synthetic-test",
  display_name: "테스트 사용자",
  role,
  region_id: null,
  is_active: true,
  version: 1,
  store_ids: ["store-one"],
  permissions: [],
});
const page = (items: unknown[], number = 1, total = items.length) => ({
  items,
  total,
  page: number,
  page_size: 100,
});
const store = { id: "store-one", name: "가상 매장", can_submit: true };
const category = { id: "category-one", name: "음료" };
function getMock(resolve: (path: string) => unknown) {
  return vi
    .spyOn(api, "get")
    .mockImplementation(async <T,>(path: string) => resolve(path) as T);
}
beforeEach(() => {
  vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  URL.createObjectURL = vi.fn(() => "blob:test-recovery");
  URL.revokeObjectURL = vi.fn();
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it("CSRF 오류에도 제출 초안과 사진을 유지하고 같은 멱등키로 명시 재전송한다", async () => {
  history.replaceState({}, "", "/store-owner/submit");
  vi.spyOn(api, "me").mockResolvedValue(account("store_owner"));
  getMock((path) =>
    path.startsWith("/stores")
      ? page([store])
      : path.startsWith("/categories")
        ? page([category])
        : page([]),
  );
  const upload = vi
    .spyOn(api, "upload")
    .mockRejectedValueOnce(
      new ApiError(403, "CSRF_INVALID", "보안 확인이 갱신되었습니다."),
    )
    .mockImplementationOnce(() => new Promise(() => {}));
  render(<App />);
  await screen.findByRole("heading", { name: "오늘의 매대, 사진으로 점검" });
  await screen.findByRole("option", { name: "가상 매장" });
  fireEvent.change(screen.getByRole("combobox", { name: /매장/ }), {
    target: { value: store.id },
  });
  fireEvent.change(screen.getByRole("combobox", { name: /매대 유형/ }), {
    target: { value: category.id },
  });
  const file = new File(["synthetic"], "my-shelf.png", { type: "image/png" });
  fireEvent.change(screen.getByLabelText(/매대 사진 선택/), {
    target: { files: [file] },
  });
  fireEvent.change(
    screen.getByRole("textbox", { name: /질문 또는 현장 상황/ }),
    { target: { value: "작성 중인 점검 질문" } },
  );
  await waitFor(() => expect((screen.getByRole("button", { name: "사진 제출하기 →" }) as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByRole("button", { name: "사진 제출하기 →" }));
  await waitFor(() => expect(upload).toHaveBeenCalledTimes(1));
  expect(await screen.findByText("보안 확인이 갱신되었습니다.")).toBeTruthy();
  expect(location.pathname).toBe("/store-owner/submit");
  expect(
    (
      screen.getByRole("textbox", {
        name: /질문 또는 현장 상황/,
      }) as HTMLTextAreaElement
    ).value,
  ).toBe("작성 중인 점검 질문");
  expect(screen.getByAltText("제출 예정 사진 1")).toBeTruthy();
  expect(upload.mock.calls[0][2][0].file).toBe(file);
  await waitFor(() => expect((screen.getByRole("button", { name: "사진 제출하기 →" }) as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByRole("button", { name: "사진 제출하기 →" }));
  await waitFor(() => expect(upload).toHaveBeenCalledTimes(2));
  expect(upload.mock.calls[1]).toEqual(upload.mock.calls[0]);
});

it.each(["content", "status"])(
  "Reference %s 충돌 복구는 최신 버전을 읽고 작성한 내용과 파일을 보존한다",
  async (change) => {
    history.replaceState({}, "", "/ofc-admin/references");
    const original = {
      id: "ref-old",
      lineage_id: "lineage-one",
      version: 1,
      state_version: 1,
      caption: "기존 설명",
      category_id: category.id,
      store_id: null,
      is_active: true,
      created_at: "2026-09-21T00:00:00Z",
      photo: {
        id: "media",
        position: 1,
        url: "/api/media/media",
        source_kind: "user_upload",
      },
    };
    const latest = {
      ...original,
      id: change === "content" ? "ref-new" : original.id,
      version: change === "content" ? 2 : 1,
      state_version: change === "content" ? 1 : 2,
      caption: "서버에서 바뀐 설명",
    };
    let changed = false;
    const get = getMock((path) =>
      path.startsWith("/stores")
        ? page([store])
        : path.startsWith("/categories")
          ? page([category])
          : path.startsWith("/regions")
            ? page([])
            : page([changed ? latest : original]),
    );
    const upload = vi
      .spyOn(api, "upload")
      .mockImplementationOnce(async () => {
        changed = true;
        throw new ApiError(
          409,
          "VERSION_CONFLICT",
          "Reference 버전이 변경되었습니다.",
        );
      })
      .mockImplementationOnce(() => new Promise(() => {}));
    render(<References account={account("hq")} />);
    fireEvent.click(
      await screen.findByRole("button", { name: "사진·설명 교체" }),
    );
    const form = screen
      .getByRole("heading", { name: "Reference 새 버전으로 교체" })
      .closest("form")!;
    fireEvent.change(
      within(form).getByRole("textbox", { name: /이 사진에서 참고할 점/ }),
      { target: { value: "나의 수정 설명" } },
    );
    fireEvent.change(within(form).getByRole("textbox", { name: /변경 사유/ }), {
      target: { value: "내 변경 사유" },
    });
    const file = new File(["synthetic"], "replacement.png", {
      type: "image/png",
    });
    fireEvent.change(within(form).getByLabelText(/매대 사진 선택/), {
      target: { files: [file] },
    });
    fireEvent.click(within(form).getByRole("button", { name: "새 버전 저장" }));
    fireEvent.click(
      await within(form).findByRole("button", { name: "최신 정보 다시 읽기" }),
    );
    await waitFor(() =>
      expect(
        get.mock.calls.filter(([path]) => path.startsWith("/references"))
          .length,
      ).toBeGreaterThan(1),
    );
    await screen.findByRole("heading", { name: "서버에서 바뀐 설명" });
    expect(
      (
        within(form).getByRole("textbox", {
          name: /이 사진에서 참고할 점/,
        }) as HTMLInputElement
      ).value,
    ).toBe("나의 수정 설명");
    expect(
      (
        within(form).getByRole("textbox", {
          name: /변경 사유/,
        }) as HTMLInputElement
      ).value,
    ).toBe("내 변경 사유");
    expect(within(form).getByAltText("제출 예정 사진 1")).toBeTruthy();
    fireEvent.click(within(form).getByRole("button", { name: "새 버전 저장" }));
    await waitFor(() => expect(upload).toHaveBeenCalledTimes(2));
    expect(upload.mock.calls[1][0]).toBe("/references/" + latest.id);
    expect(upload.mock.calls[1][1]).toEqual({
      state_version: latest.state_version,
      caption: "나의 수정 설명",
      reason: "내 변경 사유",
    });
    expect(upload.mock.calls[1][2][0].file).toBe(file);
  },
);
