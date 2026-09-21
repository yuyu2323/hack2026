import { useEffect, useState } from "react";
import { Source, type Data } from "./core";
export function PhotoPicker({
  files,
  set,
  max = 5,
}: {
  files: File[];
  set: (files: File[]) => void;
  max?: number;
}) {
  const [error, setError] = useState(""),
    [urls, setUrls] = useState<string[]>([]);
  useEffect(() => {
    const next = files.map((f) => URL.createObjectURL(f));
    setUrls(next);
    return () => next.forEach(URL.revokeObjectURL);
  }, [files]);
  return (
    <div className="photo-picker">
      <label className="upload-zone">
        <span className="upload-symbol">＋</span>
        <strong>매대 사진 선택</strong>
        <span>JPEG·PNG, 장당 10MiB 이하 · 최대 {max}장</span>
        <input
          type="file"
          accept="image/jpeg,image/png"
          multiple={max > 1}
          onChange={(e) => {
            const added = Array.from(e.target.files ?? []);
            e.target.value = "";
            if (files.length + added.length > max) {
              setError(`사진은 ${max}장까지 선택할 수 있습니다.`);
              return;
            }
            if (
              added.some(
                (f) =>
                  f.size > 10 * 1024 * 1024 ||
                  !["image/jpeg", "image/png"].includes(f.type),
              )
            ) {
              setError("JPEG·PNG, 장당 10MiB 이하 사진을 선택해 주세요.");
              return;
            }
            setError("");
            set([...files, ...added]);
          }}
        />
      </label>
      <p className="hint">
        매대 전체와 상품 앞면이 보이도록 밝은 곳에서 촬영해 주세요. 선택
        순서대로 사진 번호가 정해집니다.
      </p>
      {error && (
        <p role="alert" className="error-text">
          {error}
        </p>
      )}
      <div className="photo-grid">
        {files.map((file, index) => (
          <figure key={index}>
            <img src={urls[index]} alt={`제출 예정 사진 ${index + 1}`} />
            <figcaption>
              <strong>사진 {index + 1}</strong> · {file.name}
              <small>{(file.size / 1024 / 1024).toFixed(1)} MiB</small>
            </figcaption>
            <div className="actions">
              <button
                type="button"
                className="secondary"
                aria-label={`사진 ${index + 1} 앞으로`}
                disabled={index === 0}
                onClick={() => {
                  const next = [...files];
                  [next[index - 1], next[index]] = [
                    next[index],
                    next[index - 1],
                  ];
                  set(next);
                }}
              >
                ←
              </button>
              <button
                type="button"
                className="secondary"
                aria-label={`사진 ${index + 1} 뒤로`}
                disabled={index === files.length - 1}
                onClick={() => {
                  const next = [...files];
                  [next[index + 1], next[index]] = [
                    next[index],
                    next[index + 1],
                  ];
                  set(next);
                }}
              >
                →
              </button>
              <button
                type="button"
                className="text-button"
                onClick={() => set(files.filter((_, i) => i !== index))}
              >
                삭제
              </button>
            </div>
          </figure>
        ))}
      </div>
    </div>
  );
}
export function Photos({
  photos,
  label = "제출 사진",
  evidence = false,
}: {
  photos: Data[];
  label?: string;
  evidence?: boolean;
}) {
  return (
    <div className="photo-grid">
      {photos.map((photo, index) => (
        <ProtectedPhoto
          key={photo.id ?? photo.media_id ?? index}
          photo={photo}
          label={`${label} ${photo.position ?? index + 1}`}
          anchor={
            evidence ? "photo-" + (photo.position ?? index + 1) : undefined
          }
        />
      ))}
    </div>
  );
}
function ProtectedPhoto({
  photo,
  label,
  anchor,
}: {
  photo: Data;
  label: string;
  anchor?: string;
}) {
  const [failed, setFailed] = useState(false),
    [revision, setRevision] = useState(0);
  return (
    <figure id={anchor} className="protected-photo">
      {failed ? (
        <div className="empty">
          <p>사진을 불러오지 못했습니다.</p>
          <button
            className="secondary"
            onClick={() => {
              setFailed(false);
              setRevision((x) => x + 1);
            }}
          >
            사진 다시보기
          </button>
        </div>
      ) : (
        <a href={photo.url} target="_blank" rel="noreferrer">
          <img
            key={revision}
            src={photo.url}
            alt={label}
            onError={() => setFailed(true)}
          />
        </a>
      )}
      <figcaption>
        {label} <Source value={photo.source_kind} />
      </figcaption>
    </figure>
  );
}
