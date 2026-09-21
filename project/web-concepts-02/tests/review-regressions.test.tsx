import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import { api, type AccountMe } from "@storeloop/api-client";
import { App } from "../src/app/main";
import { Operations } from "../src/platform-admin/Operations";
import { Analytics } from "../src/ofc-admin/Analytics";
import { SubmissionDetail } from "../src/store-owner/Owner";

const account = (role: AccountMe["role"]): AccountMe => ({
  id: "safe-account",
  login_id: "synthetic-test",
  display_name: "검수 사용자",
  role,
  region_id: null,
  is_active: true,
  version: 1,
  store_ids: [],
  permissions: [],
});
const page = (items: unknown[]) => ({
  items,
  total: items.length,
  page: 1,
  page_size: 100,
});
beforeEach(() => {
  vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  history.replaceState({}, "", "/");
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
function mockGet(resolve: (path: string) => unknown) {
  return vi
    .spyOn(api, "get")
    .mockImplementation(async <T,>(path: string) => resolve(path) as T);
}

describe("독립 검수 회귀", () => {
  it("운영자 알림 직접 경로는 접근 불가이고 영업 API를 호출하지 않는다", async () => {
    history.replaceState({}, "", "/platform-admin/notifications");
    vi.spyOn(api, "me").mockResolvedValue(account("platform_operator"));
    const get = mockGet((path) =>
      path === "/announcements"
        ? page([{ id: "notice", title: "운영 공지 유지", body: "안내" }])
        : page([]),
    );
    render(<App />);
    expect(
      await screen.findByRole("heading", {
        name: "이 업무에 접근할 수 없어요",
      }),
    ).toBeTruthy();
    expect(await screen.findByText("운영 공지 유지")).toBeTruthy();
    expect(get.mock.calls.every(([path]) => path === "/announcements")).toBe(
      true,
    );
    expect(screen.queryByRole("link", { name: "알림" })).toBeNull();
  });
  it("최근 모델 사용 불가는 비교 불가와 구별한다", async () => {
    history.replaceState({}, "", "/platform-admin");
    mockGet(() => ({
      services: [],
      jobs: { queued: 0, running: 0, succeeded: 0, failed: 0 },
      fixture_jobs: { failed: 0 },
      data_quality: {
        unmapped_owner_accounts: 0,
        unmapped_ofc_accounts: 0,
        unassigned_stores: 0,
      },
      worker_heartbeat_age_seconds: null,
      model: {
        readiness: "unavailable",
        last_success_at: null,
        last_failure_at: null,
      },
    }));
    render(<Operations account={account("platform_operator")} />);
    expect(await screen.findByText("사용 불가")).toBeTruthy();
    expect(screen.queryByText("비교 불가")).toBeNull();
  });
  it("상관관계 행은 내부 UUID 대신 이름과 누락 안내를 표시한다", async () => {
    history.replaceState({}, "", "/ofc-admin/analytics");
    mockGet((path) =>
      path.startsWith("/stores")
        ? page([{ id: "store-private-uuid", name: "가상 봄빛역점" }])
        : path.startsWith("/categories")
          ? page([{ id: "category-private-uuid", name: "음료 매대" }])
          : path.startsWith("/regions")
            ? page([])
            : path.startsWith("/analytics/trends")
              ? { points: [] }
              : path.startsWith("/analytics/report")
                ? { rows: [], generated_at: null }
                : {
                    mock: true,
                    n: 2,
                    r: null,
                    reason: "insufficient_samples",
                    excluded_missing_count: 0,
                    excluded_unassessable_count: 0,
                    points: [
                      {
                        store_id: "store-private-uuid",
                        category_id: "category-private-uuid",
                        week_start: "2026-09-21",
                        compliance_rate: 50,
                        sales_amount: 100,
                        review_count: 1,
                        assessable_rate: 100,
                      },
                      {
                        store_id: "missing-private-uuid",
                        category_id: "missing-category-uuid",
                        week_start: "2026-09-21",
                        compliance_rate: 40,
                        sales_amount: 80,
                        review_count: 1,
                        assessable_rate: 100,
                      },
                    ],
                  },
    );
    render(<Analytics account={account("hq")} />);
    const table = await screen.findByRole("region", {
      name: "상관관계 관측 데이터",
    });
    expect(await within(table).findByText("가상 봄빛역점")).toBeTruthy();
    expect(within(table).getByText("음료 매대")).toBeTruthy();
    expect(within(table).getByText("매장 정보 없음")).toBeTruthy();
    expect(within(table).getByText("매대 정보 없음")).toBeTruthy();
    expect(table.textContent).not.toContain("private-uuid");
  });
  it.each([true, false])(
    "Reference 화면 번호는 snapshot 순서를 따르고 원본 사진은 보존한다 (position 포함: %s)",
    async (withPositions) => {
      history.replaceState({}, "", "/store-owner/submissions/submission");
      const detail = {
        id: "submission",
        store_name: "가상 점포",
        category_name: "음료",
        created_at: "2026-09-21T00:00:00Z",
        submitted_by_id: "another-owner",
        job: { status: "failed", error_message: "테스트용 처리 실패" },
        source_kind: "user_upload",
        photos: [],
        question: "",
        review: null,
        parent: null,
        children: [],
        issues: [],
        context: {
          guidelines: [],
          references: [
            {
              reference_id: "ref-one",
              photo_id: "media-one",
              caption: "첫 번째 참고",
              ...(withPositions ? { position: 1 } : {}),
            },
            {
              reference_id: "ref-two",
              photo_id: "media-two",
              caption: "두 번째 참고",
              ...(withPositions ? { position: 2 } : {}),
            },
          ],
        },
        reference_photos: [
          {
            reference_id: "ref-two",
            photo: {
              id: "p-two",
              media_id: "media-two",
              position: 1,
              url: "/api/media/media-two",
              source_kind: "user_upload",
            },
          },
          {
            reference_id: "ref-one",
            photo: {
              id: "p-one",
              media_id: "media-one",
              position: 1,
              url: "/api/media/media-one",
              source_kind: "ai_generated_demo",
            },
          },
        ],
      };
      const original = JSON.stringify(detail);
      const get = mockGet(() => detail);
      render(
        <SubmissionDetail id="submission" account={account("store_owner")} />,
      );
      expect(await screen.findByText("AI 생성 시연 이미지")).toBeTruthy();
      expect(
        screen
          .getAllByAltText(/비교 Reference/)
          .map((img) => img.getAttribute("src")),
      ).toEqual(["/api/media/media-one", "/api/media/media-two"]);
      expect(
        screen
          .getAllByAltText(/비교 Reference/)
          .map((img) => img.getAttribute("alt")),
      ).toEqual(["비교 Reference 1", "비교 Reference 2"]);
      expect(JSON.stringify(detail)).toBe(original);
      expect(
        get.mock.calls.every(([path]) => path === "/submissions/submission"),
      ).toBe(true);
    },
  );
  it("Reference 읽기 메타데이터가 없으면 보호 URL을 유지하고 생성 출처를 추정하지 않는다", async () => {
    history.replaceState({}, "", "/store-owner/submissions/submission");
    mockGet(() => ({
      id: "submission",
      store_name: "가상 점포",
      category_name: "음료",
      created_at: "2026-09-21T00:00:00Z",
      submitted_by_id: "another-owner",
      job: { status: "failed", error_message: "테스트용 처리 실패" },
      source_kind: "user_upload",
      photos: [],
      question: "",
      review: null,
      parent: null,
      children: [],
      issues: [],
      context: {
        guidelines: [],
        references: [
          {
            reference_id: "ref-one",
            photo_id: "media-one",
            caption: "참고 사진",
          },
        ],
      },
    }));
    render(
      <SubmissionDetail id="submission" account={account("store_owner")} />,
    );
    expect(
      (await screen.findByAltText(/비교 Reference/)).getAttribute("src"),
    ).toBe("/api/media/media-one");
    expect(screen.queryByText("AI 생성 시연 이미지")).toBeNull();
  });
});
