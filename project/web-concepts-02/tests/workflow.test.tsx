import { describe, it, expect, afterEach, beforeAll, vi } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { JobStatus } from "../src/shared/JobStatus";
import { rate, safeReturn } from "../src/shared/core";
beforeAll(() => {
  URL.createObjectURL = vi.fn(() => "blob:local-test");
  URL.revokeObjectURL = vi.fn();
});
afterEach(cleanup);
describe("업무 의미와 접근 경계", () => {
  it("판단 불가 점수를 0으로 표시하지 않는다", () => {
    expect(rate(null)).toBe("—");
    expect(rate(0)).toBe("0%");
  });
  it("로그인 복귀 경로는 같은 역할 경로만 허용한다", () => {
    expect(safeReturn("/platform-admin/accounts", "store_owner")).toBe(
      "/store-owner",
    );
    expect(safeReturn("//evil.test", "hq")).toBe("/ofc-admin");
    expect(
      safeReturn("/store-owner/history?store_id=one", "store_owner"),
    ).toContain("/store-owner/history");
  });
  it("30초 넘는 분석을 실패라고 안내하지 않는다", () => {
    render(
      <JobStatus
        job={{ status: "running", delayed: true, elapsed_ms: 36000 }}
      />,
    );
    expect(screen.getByText(/분석에 시간이 더 필요해요/)).toBeTruthy();
    expect(screen.queryByText(/완료하지 못했어요/)).toBeNull();
  });
  it("기술 실패에는 안전한 설명과 운영자 복구 동선을 표시한다", () => {
    render(
      <JobStatus
        job={{
          status: "failed",
          error_message: "처리 연결을 확인해 주세요.",
          error_code: "AI_UNAVAILABLE",
        }}
      />,
    );
    expect(screen.getByText("처리 연결을 확인해 주세요.")).toBeTruthy();
    expect(screen.getByText(/운영자/)).toBeTruthy();
  });
});

describe("사진 입력 경계", () => {
  it("사진 장수 제한을 넘으면 선택을 보존한다", async () => {
    const { PhotoPicker } = await import("../src/shared/photos");
    const { fireEvent } = await import("@testing-library/react");
    const set = vi.fn();
    render(<PhotoPicker files={[]} set={set} max={1} />);
    const a = new File(["a"], "a.png", { type: "image/png" }),
      b = new File(["b"], "b.png", { type: "image/png" });
    fireEvent.change(screen.getByLabelText(/매대 사진 선택/), {
      target: { files: [a, b] },
    });
    expect(screen.getByRole("alert").textContent).toContain("1장까지");
    expect(set).not.toHaveBeenCalled();
  });
  it("지원하지 않는 파일을 제출 목록에 추가하지 않는다", async () => {
    const { PhotoPicker } = await import("../src/shared/photos");
    const { fireEvent } = await import("@testing-library/react");
    const set = vi.fn();
    render(<PhotoPicker files={[]} set={set} />);
    fireEvent.change(screen.getByLabelText(/매대 사진 선택/), {
      target: { files: [new File(["x"], "x.svg", { type: "image/svg+xml" })] },
    });
    expect(screen.getByRole("alert").textContent).toContain("JPEG·PNG");
    expect(set).not.toHaveBeenCalled();
  });
});

it("역할 밖으로 정규화되는 복귀 경로를 차단한다", () => {
  expect(safeReturn("/store-owner/../platform-admin", "store_owner")).toBe(
    "/store-owner",
  );
  expect(safeReturn("/store-owner/%2e%2e/platform-admin", "store_owner")).toBe(
    "/store-owner",
  );
});

it('수정 충돌에 입력을 유지하며 최신 정보를 읽는 행동을 제공한다', async () => {
  const { ActionForm, ApiError } = await import('../src/shared/core');
  const { fireEvent } = await import('@testing-library/react');
  render(<ActionForm title="변경" initial={{name:'내 입력'}} fields={[{name:'name',label:'이름'}]} submit={async()=>{throw new ApiError(409,'VERSION_CONFLICT','버전이 바뀌었습니다.')}}/>);
  fireEvent.click(screen.getByRole('button',{name:'변경 저장'}));
  expect(await screen.findByRole('button',{name:'최신 정보 다시 읽기'})).toBeTruthy();
  expect((screen.getByLabelText('이름') as HTMLInputElement).value).toBe('내 입력');
});
