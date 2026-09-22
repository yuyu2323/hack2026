import { useEffect, useRef, useState } from "react";
import { Source, type Data } from "./core";
import { prepareHostedPhoto } from "./hosted-photo";
import { rolePhotoUrl } from "./demo-role";
const hostedUploads = import.meta.env.VITE_HOSTED_UPLOAD_LIMIT === "true";
export function PhotoPicker({
  files,
  set,
  max = 5,
  demoSample = false,
  onBusyChange,
}: {
  files: File[];
  set: (files: File[]) => void;
  max?: number;
  demoSample?: boolean;
  onBusyChange?: (busy: boolean) => void;
}) {
  const [busy, setBusy] = useState(false);
  const processing = useRef(false);
  const [error, setError] = useState(""),
    [urls, setUrls] = useState<string[]>([]);
  async function addFiles(added: File[]) {
if (!added.length) return;
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
setBusy(true);
try {
  const prepared: File[] = [];
  for (const file of added) {
    prepared.push(hostedUploads ? await prepareHostedPhoto(file, max) : file);
  }
  set([...files, ...prepared]);
} catch {
  setError("사진을 처리할 수 없습니다. 크기를 줄이거나 다른 JPEG·PNG 사진을 선택해 주세요.");
} finally {
  setBusy(false);
}
  }
  async function receiveFiles(read: () => Promise<File[]>) {
    if (processing.current) return;
    processing.current = true;
    onBusyChange?.(true);
    setBusy(true);
    setError("");
    try {
      const added = await read();
      if (!added.length) setError("클립보드에 이미지가 없습니다. 사진 자체를 복사한 뒤 다시 시도해 주세요.");
      else await addFiles(added);
    } catch {
      setError("클립보드를 읽을 수 없습니다. 브라우저 권한을 허용하거나 Ctrl+V / ⌘V로 붙여넣어 주세요.");
    } finally {
      processing.current = false;
      onBusyChange?.(false);
      setBusy(false);
    }
  }
  useEffect(() => {
    function paste(event: ClipboardEvent) {
      const target = event.target;
      if (target instanceof HTMLElement && target.closest("input, textarea, [contenteditable]:not([contenteditable='false'])")) return;
      const images = Array.from(event.clipboardData?.items ?? [])
        .filter((item) => item.kind === "file" && item.type.startsWith("image/"))
        .map((item) => item.getAsFile()).filter((file): file is File => file !== null);
      if (!images.length) return;
      event.preventDefault();
      void receiveFiles(async () => images);
    }
    document.addEventListener("paste", paste);
    return () => document.removeEventListener("paste", paste);
  });
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
          disabled={busy}
          onChange={async (e) => {
            const added = Array.from(e.target.files ?? []);
            e.target.value = "";
            if (!added.length) return;
            await receiveFiles(async () => added);
          }}
        />
      </label>
      <button type="button" className="secondary" disabled={busy || files.length >= max} onClick={() => void receiveFiles(async () => {
        if (!navigator.clipboard?.read) throw new Error("클립보드 읽기 미지원");
        const items = await navigator.clipboard.read();
        const images: File[] = [];
        for (const item of items) {
          const type = item.types.find((value) => ["image/png", "image/jpeg"].includes(value));
          if (type) images.push(new File([await item.getType(type)], `붙여넣은 사진 ${images.length + 1}.${type === "image/png" ? "png" : "jpg"}`, { type }));
        }
        return images;
      })}>클립보드 이미지 붙여넣기</button>
      <p className="hint">사진을 복사한 뒤 이 화면에서 Ctrl+V / ⌘V로 붙여넣을 수도 있습니다. 글 입력 중에는 버튼을 사용해 주세요.</p>
      {demoSample && <button type="button" className="secondary" disabled={busy || files.length >= max} onClick={async () => {
        if (processing.current) return;
        processing.current = true;
        onBusyChange?.(true);
        setBusy(true); setError("");
        try {
          const response = await fetch("/demo-beverage.png");
          if (!response.ok) throw new Error("시연 사진 요청 실패");
          const blob = await response.blob();
          await addFiles([new File([blob], "AI 생성 시연 사진.png", { type: "image/png" })]);
        } catch { setError("시연 사진을 불러오지 못했습니다. 다시 시도해 주세요."); }
        finally { processing.current = false; onBusyChange?.(false); setBusy(false); }
      }}>시연 사진 사용</button>}
      <p className="hint">
        매대 전체와 상품 앞면이 보이도록 밝은 곳에서 촬영해 주세요. 선택
        순서대로 사진 번호가 정해집니다.
      </p>
      {hostedUploads && <p className="hint">큰 사진은 업로드에 맞게 자동으로 줄입니다. 아래 미리보기가 전송됩니다.</p>}
      {busy && <p role="status">사진을 준비하고 있습니다…</p>}
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
                disabled={busy || index === 0}
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
                disabled={busy || index === files.length - 1}
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
                disabled={busy}
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
        <a href={rolePhotoUrl(photo.url)} target="_blank" rel="noreferrer">
          <img
            key={revision}
            src={rolePhotoUrl(photo.url)}
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
