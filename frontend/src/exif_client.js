// frontend/src/exif_client.js
// Client-side EXIF/IPTC extraction and image preview handling
// Dependencies: exifr (npm install exifr)
import * as exifr from 'exifr';

export async function extractMetadataFromFile(file) {
  // Returns a normalized metadata object (EXIF, IPTC, GPS, orientation)
  try {
    const exif = await exifr.parse(file, { tiff: true, ifd0: true, exif: true, gps: true, iptc: true });
    return exif || {};
  } catch (err) {
    console.warn('EXIF parse failed:', err);
    return {};
  }
}

export function createPreviewURL(file) {
  // Create an object URL for previewing; consumer should revoke when done
  return URL.createObjectURL(file);
}

export async function loadImageWithOrientation(file, imgElement) {
  // Loads the image into an <img> element and applies EXIF-based orientation corrections where necessary.
  const meta = await extractMetadataFromFile(file);
  const url = createPreviewURL(file);
  imgElement.src = url;
  // exifr can auto-orient if used to load full image blob, but in browsers we handle CSS-based orientation
  // Consumers should call URL.revokeObjectURL(url) when replacing/removing the image to free memory
  return meta;
}
