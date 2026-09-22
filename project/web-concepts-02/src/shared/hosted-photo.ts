// 서버리스 요청 크기를 넘는 사진만 전송 전에 줄인다.
export const HOSTED_PHOTO_BYTES = Math.floor(3.5 * 1024 * 1024);
export async function prepareHostedPhoto(file: File, maxPhotos: number): Promise<File> {
  const budget = Math.floor(HOSTED_PHOTO_BYTES / maxPhotos);
  if (file.size <= budget) return file;
  const bitmap = await createImageBitmap(file);
  try {
    const scale = Math.min(1, 1800 / Math.max(bitmap.width, bitmap.height));
    let width = Math.max(32, Math.round(bitmap.width * scale));
    let height = Math.max(32, Math.round(bitmap.height * scale));
    const canvas = document.createElement("canvas");
    for (let step = 0; step < 5; step++) {
      canvas.width = width; canvas.height = height;
      const context = canvas.getContext("2d");
      if (!context) throw new Error("사진을 처리할 수 없습니다.");
      context.fillStyle = "white";
      context.fillRect(0, 0, width, height);
      context.drawImage(bitmap, 0, 0, width, height);
      for (const quality of [0.88, 0.76, 0.64]) {
        const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", quality));
        if (blob && blob.size <= budget) {
          return new File([blob], file.name.replace(/\.[^.]+$/, "") + ".jpg", { type: "image/jpeg", lastModified: file.lastModified });
        }
      }
      width = Math.max(32, Math.round(width * 0.8));
      height = Math.max(32, Math.round(height * 0.8));
    }
    throw new Error("사진 크기를 줄여 다시 선택해 주세요.");
  } finally {
    bitmap.close();
  }
}
