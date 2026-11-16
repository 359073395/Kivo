/** Display streamed output in short batches instead of re-rendering the app per character. */
export const STREAM_FRAME_MS = 33;

export function streamFrameLength(buffer: string): number {
  let length = Math.min(buffer.length, Math.max(4, Math.ceil(buffer.length / 6)));
  // A frame must not expose half an emoji/supplementary character.
  const last = buffer.charCodeAt(length - 1);
  const next = buffer.charCodeAt(length);
  if (last >= 0xd800 && last <= 0xdbff && next >= 0xdc00 && next <= 0xdfff) length++;
  return length;
}
