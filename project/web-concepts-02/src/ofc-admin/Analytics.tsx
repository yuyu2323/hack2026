import type { AccountMe, Page } from "@storeloop/api-client";
import {
  Badge,
  businessQuery,
  date,
  Empty,
  FilterBar,
  PageTitle,
  Panel,
  rate,
  Resource,
  type Data,
  useLocation,
  useResource,
} from "../shared/core";
export function Analytics({ account }: { account: AccountMe }) {
  const { search, query } = useLocation();
  const stores = useResource<Page<Data>>("/stores?page_size=100");
  const categories = useResource<Page<Data>>("/categories?page_size=100");
  const storeNames = new Map(
    stores.data?.items.map((item) => [item.id, item.name]) ?? [],
  );
  const categoryNames = new Map(
    categories.data?.items.map((item) => [item.id, item.name]) ?? [],
  );
  const filters = businessQuery(search);
  const group = query.get("group_by") ?? "store";
  const trends = useResource<Data>("/analytics/trends" + filters),
    correlation = useResource<Data>("/analytics/correlation" + filters),
    report = useResource<Data>(
      "/analytics/report" +
        filters +
        (filters ? "&" : "?") +
        "group_by=" +
        group,
    );
  return (
    <>
      <PageTitle
        title="작은 개선이 어떻게 이어졌을까요?"
        description="기간별 점검 추이와 Mock 매출의 관계를 함께 살펴보세요."
      />
      <FilterBar
        account={account}
        extra={[
          {
            name: "group_by",
            label: "리포트 묶음",
            type: "select",
            options: [
              { id: "store", name: "매장" },
              { id: "region", name: "지역" },
              { id: "category", name: "매대 유형" },
            ],
          },
        ]}
      />
      <Panel title="주간 점검 추이">
        <Resource value={trends}>
          {(data: Data) =>
            data.points.length ? (
              <>
                <div
                  className="bar-chart"
                  role="img"
                  aria-label="주간 준수율 막대그래프. 자세한 값은 아래 데이터 표에서 확인할 수 있습니다."
                >
                  {data.points.map((p: Data) => (
                    <div className="bar-item" key={p.week_start}>
                      <strong>{rate(p.compliance_rate)}</strong>
                      <div className="bar-space">
                        {p.compliance_rate == null ? (
                          <span className="null-chart">판단 불가</span>
                        ) : (
                          <span
                            className="bar"
                            style={{ height: p.compliance_rate + "%" }}
                          />
                        )}
                      </div>
                      <small>{p.week_start.slice(5)}</small>
                    </div>
                  ))}
                </div>
                <div
                  className="table-scroll"
                  tabIndex={0}
                  role="region"
                  aria-label="주간 추이 데이터 표"
                >
                  <table>
                    <thead>
                      <tr>
                        <th>주 시작</th>
                        <th>제출</th>
                        <th>평가</th>
                        <th>준수율</th>
                        <th>판단 가능률</th>
                        <th>판단 불가 기준</th>
                        <th>Mock 평가</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.points.map((p: Data) => (
                        <tr key={p.week_start}>
                          <td>{p.week_start}</td>
                          <td>{p.submission_count}</td>
                          <td>{p.review_count}</td>
                          <td>{rate(p.compliance_rate)}</td>
                          <td>{rate(p.assessable_rate)}</td>
                          <td>{p.unknown_count}</td>
                          <td>{p.mock_review_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <Empty>선택한 기간의 추이 데이터가 없습니다.</Empty>
            )
          }
        </Resource>
      </Panel>
      <Panel title="준수도와 매출의 상관관계">
        <Badge tone="mock">Mock 데이터</Badge>
        <p>
          같은 매장·매대·주차의 유효한 관측값을 비교합니다. 상관관계는 원인이나
          매출 예측을 의미하지 않습니다.
        </p>
        <Resource value={correlation}>
          {(data: Data) => (
            <>
              <div className="review-summary">
                <div>
                  <span>Pearson r</span>
                  <strong>{data.r ?? "—"}</strong>
                </div>
                <div>
                  <span>유효 표본</span>
                  <strong>{data.n}쌍</strong>
                </div>
                <div>
                  <span>제외</span>
                  <strong>
                    {data.excluded_missing_count +
                      data.excluded_unassessable_count}
                    건
                  </strong>
                </div>
              </div>
              {data.reason && (
                <p className="notice">
                  {data.reason === "insufficient_samples"
                    ? "표본이 부족해 계산할 수 없습니다."
                    : "값의 변화가 없어 계산할 수 없습니다."}
                </p>
              )}
              <p>
                매출·준수도 결측 제외 {data.excluded_missing_count}건 · 판단
                불가 제외 {data.excluded_unassessable_count}건
              </p>
              {data.points.length > 0 && <Scatter points={data.points} />}
              <div
                className="table-scroll"
                tabIndex={0}
                role="region"
                aria-label="상관관계 관측 데이터"
              >
                <table>
                  <thead>
                    <tr>
                      <th>매장 / 매대</th>
                      <th>주 시작</th>
                      <th>준수율</th>
                      <th>Mock 매출</th>
                      <th>평가수</th>
                      <th>판단 가능률</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.points.map((p: Data, i: number) => (
                      <tr key={i}>
                        <td>
                          <span>
                            {storeNames.get(p.store_id) ?? "매장 정보 없음"}
                          </span>
                          <br />
                          <span>
                            {categoryNames.get(p.category_id) ??
                              "매대 정보 없음"}
                          </span>
                        </td>
                        <td>{p.week_start}</td>
                        <td>{rate(p.compliance_rate)}</td>
                        <td>
                          {Number(p.sales_amount).toLocaleString("ko-KR")}원
                        </td>
                        <td>{p.review_count}</td>
                        <td>{rate(p.assessable_rate)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </Resource>
      </Panel>
      <Panel title="선택한 기간의 운영 리포트">
        <Resource value={report}>
          {(data: Data) => (
            <>
              <p>
                생성 {date(data.generated_at)} ·{" "}
                <Badge tone="mock">매출은 Mock 데이터</Badge>
              </p>
              {data.rows.length ? (
                <div
                  className="table-scroll"
                  tabIndex={0}
                  role="region"
                  aria-label="기간별 운영 리포트"
                >
                  <table>
                    <thead>
                      <tr>
                        <th>대상</th>
                        <th>제출</th>
                        <th>평가</th>
                        <th>기술 실패</th>
                        <th>미해결</th>
                        <th>준수율</th>
                        <th>판단 가능률</th>
                        <th>Mock 매출</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.rows.map((r: Data) => (
                        <tr key={r.id}>
                          <th>{r.name}</th>
                          <td>{r.submission_count}</td>
                          <td>{r.review_count}</td>
                          <td>{r.failed_count}</td>
                          <td>{r.open_issue_count}</td>
                          <td>{rate(r.compliance_rate)}</td>
                          <td>{rate(r.assessable_rate)}</td>
                          <td>
                            {r.mock_sales_amount == null
                              ? "—"
                              : Number(r.mock_sales_amount).toLocaleString(
                                  "ko-KR",
                                ) + "원"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <Empty />
              )}
            </>
          )}
        </Resource>
      </Panel>
    </>
  );
}
function Scatter({ points }: { points: Data[] }) {
  const max = Math.max(...points.map((p) => Number(p.sales_amount)), 1);
  return (
    <figure className="scatter">
      <svg viewBox="0 0 640 260" role="img" aria-labelledby="scatter-title">
        <title id="scatter-title">
          준수율과 Mock 매출 산점도. 같은 매장·매대·주차의 관측값이며 아래 표에
          모든 수치가 있습니다.
        </title>
        <path d="M60 20V215H620" fill="none" stroke="currentColor" />
        {[0, 25, 50, 75, 100].map((x) => (
          <g key={x}>
            <path d={`M${60 + x * 5.5} 20V215`} stroke="#dde3db" />
            <text x={60 + x * 5.5} y="237" textAnchor="middle">
              {x}%
            </text>
          </g>
        ))}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={60 + p.compliance_rate * 5.5}
            cy={210 - (Number(p.sales_amount) / max) * 180}
            r="5"
            fill="#224d3b"
            opacity=".7"
          >
            <title>
              {p.week_start} · 준수율 {p.compliance_rate}% · Mock 매출{" "}
              {p.sales_amount}원
            </title>
          </circle>
        ))}
        <text x="10" y="20">
          매출
        </text>
        <text x="580" y="258">
          준수율
        </text>
      </svg>
    </figure>
  );
}
